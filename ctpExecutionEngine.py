'''The execution engine for CTP interface.
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
import logging
import yaml

# third-party modules
import gevent

# customized modules
import ctptrader
import ctpOrder
import ctpUtil
import execution.engine as eEngine

# initialize logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s', level=logging.INFO )


class CTPExecutionEngine( eEngine.ExecutionEngine ):
    '''The CTP specific execution engine.
    '''
    def __init__( self, configPath ):
        '''Initialize the trader engine.

Parameters
----------
configPath : str
    path to the configure for the data feed including fields
    TRADER_FRONT_IP : str
        gateway IP address;
    BROKER_ID : str
        broker ID;
    INVESTOR_ID : str
        investor ID;
    PASSOWRD : str
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

        # login CTP trader API
        ctptrader.login( self.config[ 'TRADER_FRONT_IP' ],
                self.config[ 'BROKER_ID' ], self.config[ 'INVESTOR_ID' ],
                self.config[ 'PASSWORD' ], self._onRspUserLogin,
                self._onOrderSubmitted, self._onOrderActionTaken,
                self._onOrderReturn, self._onTradeReturn )

        self.executedOrders = {}

        # next order identifier
        self.nextId = 1

        # callbacks
        self.onRspUserLogin   = None
        self.onOrderSubmitted = None
        self.onOrderActionTaken = None
        self.onOrderReturn = None
        self.onTradeReturn = None


    def setCallbacks( self, onRspUserLogin=None, onOrderSubmitted=None,
            onOrderActionTaken=None, onOrderReturn=None, onTradeReturn=None ):
        '''Set callback functions for later processing.

Parameters
----------
onRspUserLogin : callable
    Callback function to response user login, None by default;
onOrderSubmitted : callable
    Callback function to response order submit, None by default;
onOrderActionTaken : callable
    Callback function to acknowledge order action taken, None by default;
onOrderReturn : callable
    Callback function to response order return, None by default;
onTradeReturn : callable
    Callback function to response trade return, None by default;
        '''
        self.onRspUserLogin   = onRspUserLogin
        self.onOrderSubmitted = onOrderSubmitted
        self.onOrderActionTaken = onOrderActionTaken
        self.onOrderReturn = onOrderReturn
        self.onTradeReturn = onTradeReturn


    def connect( self ):
        '''Bring the CTP execution engine online.
        '''
        ctptrader.connect()


    def placeOrder( self, order, onOrderFilled=None ):
        '''Submit the order to the CTP engine.

Parameters
----------
order : ctpOrder.CTPOrder
    an CTP compatible order.
onOrderFilled : callable
    the callback if given, when the submitted order is filled.

Returns
-------
orderId : ctpOrder.CTPOrderId
    identifier of the CTP order;
        '''
        orderId = self.nextId
        self.nextId += 1

        ctpOrderObj = ctpUtil.convertToCtpOrder( order )
        ctptrader.placeOrder( ctpOrderObj, orderId )

        orderId = ctpOrder.CTPOrderId( order.secId, ctpOrderObj.exch,
                orderId )
        return orderId


    def cancelOrder( self, orderId ):
        '''Cancel the given order through the CTP interface.

Parameters
----------
orderId : ctpOrder.CTPOrderId
    identifier of the CTP order to cancel.

Returns
-------
orderStatus : ctpOrder.CTPOrderStauts
    Status of the CTP order.
        '''
        ctptrader.cancelOrder( orderId )


    def queryStatus( self, orderId ):
        '''Query status of the CTP order.

Parameters
----------
orderId : ctpOrder.CTPOrderId
    identifier of the CTP order to query.

Returns
-------
orderStatus : ctpOrder.CTPOrderStatus
    Status of the CTP order.
        '''


    def updateOrder( self, orderId, newOrder ):
        '''Update the order associated with the given order identifier to the new order.

Parameters
----------
orderId : ctpOrder.CTPOrderId
    identifier of the CTP order to query;
newOrder : ctpOrder.CTPOrder
    the new CTP order object to update.

Returns
-------
orderStatus : ctpOrder.CTPOrderStatus
    Status of the CTP order.
        '''

    def _onRspUserLogin( self ):
        '''Callbacks for user login.
        '''
        logging.info( 'CTP trader logged in.' )


    def _onOrderSubmitted( self, orderId, requestId ):
        '''Callbacks for order filled.

Parameters
----------
orderId : int
    Order identifier for the given order;
requestId : int
    request identifier for the given order.
        '''
        print( 'order submitted', orderId, requestId )

        
    def _onOrderActionTaken( self, orderId, requestId ):
        '''Callbacks for order action taken.

Parameters
----------
orderId : int
    The identifier of the order where the action is taken;
requestId : int
    request identifier for the given order.
        '''


    def _onOrderReturn( self, orderRefId, notifySeq, orderStatus, volumeTraded,
            volumeTotal, seqNo ):
        '''Callbacks for order return.

Parameters
----------
orderRefId : str
    Order reference ID;
notifySeq : int
    notify sequence;
orderStatus : int
    the status of orders;
volumeTraded : int
    volumes filled;
volumeTotal : int
    volumes in total;
seqNo : int
    sequence number.
        '''


    def _onTradeReturn( self, orderRefId, orderSysId, tradeId, price, volume,
            tradeDate, tradeTime, orderLocalId, seqNo ):
        '''Callbacks for trade return.

Parameters
----------
orderRefId : str
    Order reference ID;
orderSysId : str
    order system ID;
tradeId : str
    trade identifier;
price : float
    trade price;
volume : int
    trade volume;
tradeDate : str
    trade date;
tradeTime : str
    trade time;
orderLocalId : str
    local order ID;
seqNo : int
    sequence number.
        '''
        if self.onTradeReturn is not None:
            self.onTradeReturn( orderRefId, orderSysId, tradeId, price, volume,
                    tradeDate, tradeTime, orderLocalId, seqNo )
