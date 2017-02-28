# -*- coding: utf-8 -*-

'''CTP compatible bullet order.
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

# third-party modules

# customized modules
import execution.order as eo

class CTPOrder( eo.Order ):
    '''An implementation of CTP compatible bullet order.
    '''

    # Offset flags
    OFFSET_OPEN  = 48     # ASCII code of '0'
    OFFSET_CLOSE = 49
    OFFSET_FORCE_CLOSE = 50
    OFFSET_CLOSE_TODAY = 51
    OFFSET_CLOSE_YSTDY = 52
    OFFSET_FORCE_OFF   = 53
    OFFSET_LOCAL_FORCE_CLOSE = 54


    # Side flags
    DIRECTION_BUY  = 48     # ASCII code of '0'
    DIRECTION_SELL = 49


    # Price type type
    PRICE_ANY_PRICE   = 49  # ASCII code of '1'
    PRICE_LIMIT_PRICE = 50
    PRICE_BEST_PRICE  = 51

    PRICE_LAST_PRICE  = 52
    PRICE_LAST_PRICE_PLUS_ONE_TICK   = 53
    PRICE_LAST_PRICE_PLUS_TWO_TICK   = 54
    PRICE_LAST_PRICE_PLUS_THREE_TICK = 55

    PRICE_ASK_PRICE1  = 56
    PRICE_ASK_PRICE1_PLUS_ONE_TICK   = 57
    PRICE_ASK_PRICE1_PLUS_TWO_TICK   = 65
    PRICE_ASK_PRICE1_PLUS_THREE_TICK = 66

    PRICE_BID_PRICE1  = 67
    PRICE_BID_PRICE1_PLUS_ONE_TICK   = 68
    PRICE_BID_PRICE1_PLUS_TWO_TICK   = 69
    PRICE_BID_PRICE1_PLUS_THREE_TICK = 70


    def __init__( self, instId, exch, side, volume, priceType, price,
            offsetFlag ):
        super( CTPOrder, self ).__init__( instId, side, volume, price )

        self.exch       = exch
        self.offsetFlag = offsetFlag
        self.priceType  = priceType


class CTPOrderStatus( eo.OrderStatus ):
    '''An implementation of CTP compatible order status.
    '''
    ORDER_SUBMITTED        = 48        # ASCII code of '0'
    ORDER_CANCEL_SUBMITTED = 49
    ORDER_MODIFY_SUBMITTED = 50
    ORDER_ACCEPTED         = 51
    ORDER_REJECTED         = 52
    ORDER_CANCEL_REJECTED  = 53
    ORDER_MODIFY_REJECTED  = 54

    def __init__( self, sessionId, status ):
        '''Initialize order status.
        '''
        super( CTPOrderStatus, self ).__init__()

        self.sessionId = sessionId
        self.status    = status


class CTPOrderId( eo.OrderId ):
    '''An implementation of CTP compatible order identifier object.
    '''
    def __init__( self, instId, exchange, orderId ):
        '''Initialize CTP order identifier.
        '''
        super( CTPOrderId, self ).__init__( orderId )

        self.instId   = instId
        self.exchange = exchange
        self.orderId  = orderId 
