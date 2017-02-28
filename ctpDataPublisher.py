'''A data feed engine for CTP bridge.
'''

'''
Copyright (c) 2017, WinQuant Information and Technology Co. Ltd.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

# built-in modules
import datetime as dt
import logging
import time
import yaml

# third-party modules
import threading
import pandas as pd
import zmq.green as zmq

# customized modules
import datafeed.engine  as dEngine
import ctpmd
import ctpUtil

# customize logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s',
        level=logging.DEBUG )

class CTPDataPublisher( dEngine.DataPublisher ):
    '''Data publisher engine for CTP.
    '''
    def __init__( self, configPath ):
        '''Initialize the data publisher.

Parameters
----------
configPath : str
    path to the configure for the data feed including fields
    MD_FRONT_ID : str
        gateway IP address;
    BROKER_ID : str
        broker ID;
    INVESTOR_ID : str
        investor ID;
    PASSWORD : str
        password to authenticate.

    The configure file is encoded as a YAML.

Exceptions
----------
raise
* FileNotFoundError when the given YAML file is not found;
* KeyError if the required fileds are not specified in the configure file.
        '''
        with open( configPath, 'r' ) as f:
            self.config = yaml.load( f.read() )
        # initialize the subscriber dict
        self.subscribers = {}

        # mapping from CTP securities ID's to external names
        self.secIds = {}
        # mapping from instrument to concerned
        self.topicsToSubscribers = {}

        # next identifier for the subscriber
        self.nextId = 1

        ctpmd.login( self.config[ 'MD_FRONT_IP' ], self.config[ 'BROKER_ID' ],
                self.config[ 'INVESTOR_ID' ], self.config[ 'PASSWORD' ] )


    def connect( self, startDate=dt.date( 2012, 1, 1 ), endDate=dt.date.today() ):
        '''Put the data feed engine online and subscribes to the interested topics.

Parameters
----------
startDate : datetime.date
    start date of the backtesting;
endDate : datetime.date
    end date of the backtesting.
        '''
        # summarise all the messages to subscribe
        fields = set()
        for _, s in self.subscribers.items():
            t = s.getSubscribedTopics()
            f = s.getSubscribedDataFields()
            # In case the passed in symbols are securities ID's.
            ctpTopics = dict( ( ctpUtil.getCtpInstId( tt ), tt ) for tt in t )
            self.secIds.update( ctpTopics )
            if not ( f is None or fields is None ):
                fields.update( f )
            else:
                fields = None

        topics = self.secIds.keys()

        logging.info( 'Subscribe data for {ts:s} and {fs:s}.'.format(
                ts=', '.join( list( topics ) ),
                fs=', '.join( list( fields ) ) if fields is not None else 'ALL' ) )

        ctpmd.connect( self.config[ 'MQ_PUB_ADDR' ] )
        logging.info( 'Waiting connection to establish...' )
        time.sleep( 1 )

        logging.info( 'Setting-up receiver...' )
        # set up the receiver
        receiver = threading.Thread( target=self.receiveDatafeed, args=( topics, ) )

        # subscribe to the market data
        ctpmd.subscribeMarketData( list( topics ) )

        # wait the event thread to exit
        # receiver.join()
        return receiver


    def addSubscriber( self, subscriber ):
        '''Add subscriber to this publisher.

Parameters
----------
subscriber : datafeed.subscriber.Subscriber
    Add subscriber to the data publisher.

Returns
-------
subscriberId : int
    Identifier of the subscriber.
        '''
        if subscriber is not None:
            subId = self.nextId
            self.nextId += 1

            self.subscribers[ subId ] = subscriber

            # add the subscriber to the topics to subscribers mapping
            subscribedTopics = subscriber.getSubscribedTopics()
            for topic in subscribedTopics:
                if topic not in self.topicsToSubscribers:
                    self.topicsToSubscribers[ topic ] = set()

                logging.debug( 'Add subscriber {sid:d} to topic {t:s}.'.format(
                        sid=subId, t=topic ) )
                self.topicsToSubscribers[ topic ].add( subscriber )
        else:
            subId = None

        return subId


    def removeSubscriber( self, subscriberId ):
        '''Drop a given subscriber from the publisher.

Parameters
----------
subscriberId : int
    Identifier of the subscriber.

Returns
-------
subscriber : datafeed.subscriber.Subscriber
    Dropped subscriber.

Exceptions
----------
raise Exception when error occurs.
        '''
        if subscriberId not in self.subscribers:
            raise Exception( 'Requested subscriber does not exist.' )
        else:
            subscriber = self.subscribers.pop( subscriberId, None )

            if subscriber is not None:
                # drop the subscriber from the topic to subscribers mapping
                subscribedTopics = subscriber.getSubscribedTopics()
                for topic in subscribedTopics:
                    logging.debug( 'Remove subscriber {sid:d} from topic list {t:s}.'.format(
                            sid=subscriberId, t=topic ) )
                    self.topicsToSubscribers[ topic ] -= { subscriber, }

            return subscriber


    def notify( self, subscriberId, data ):
        '''Notify one subscriber by the subscriber ID.

Parameters
----------
subscriberId : int
    Identifier of the subscriber;
data : pandas.DataFrame
    data in pandas.DataFrame feed to the subscriber.

Returns
-------
None.

Exceptions
----------
raise Exception when error occurs.
        '''
        if subscriberId in self.subscribers:
            self.subscribers[ subscriberId ].onData( data )
        else:
            raise Exception( 'Subscriber with ID {sid:d} does not exist.'.format(
                    sid=subscriberId ) )


    def notifyAll( self, data ):
        '''Notify all subscribers with the given data.

Parameters
----------
data : object
    data feed to all the subscribers.

Exceptions
----------
raise Exception when error occurs.
        '''
        # find all the subscribers that care about the datafeed.
        secIds = set( data.index )
        subscribers = set()
        for secId in secIds:
            subscribers = subscribers.union( self.topicsToSubscribers.get( secId, set() ) )

        if len( subscribers ) > 0:
            for s in subscribers:
                s.onData( data )


    def receiveDatafeed( self, topics ):
        '''Receive datafeed from the data publisher.

Parameters
----------
topics : list of str
    topics that the receiver concerns.
        '''
        ctx  = zmq.Context()
        sock = ctx.socket( zmq.SUB )
        # add concerned topics
        for topic in topics:
            sock.setsockopt_string( zmq.SUBSCRIBE, topic )

        # let's connect to the publisher
        sock.connect( self.config[ 'MQ_SUB_ADDR' ] )

        while True:
            # decode raw data
            raw  = sock.recv().decode( 'utf-8' )
            cols = [ 'secId', 'tradeDate', 'price' ]
            instId, tradeDatetime, price = raw.split( ',' )
            data = [ self.secIds.get( instId, instId ),
                     dt.datetime.strptime( tradeDatetime, '%Y%m%d %H:%M:%S' ),
                     float( price ) ]

            if len( data ) == len( cols ):
                # required data are all available
                df   = pd.DataFrame( dict( zip( cols, data ) ), index=[ 0 ] )
                df.set_index( 'secId', inplace=True )
                self.notifyAll( df )
            else:
                logging.warning( 'Received data {rd:s} which is not enough to use.'.format(
                        rd=raw ) )
