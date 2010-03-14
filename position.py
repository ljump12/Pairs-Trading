class Order:

    def __init__(self, Symbol, Side, Type, Price, Shares):
        self.Symbol 					= Symbol    ## (AAPL, MSFT, ...)
        self.Side                       = Side      ## (B, S)
        self.Type                       = Type      ## Market / Limit / Stop
        self.Price                      = Price     ##
        self.Shares                     = Shares    ## 100, 1000, 1342 etc.
        self.ExecPrice                  = None ## The price the order was executed at.
    
    def getSide(self):
        return self.Side

    def getType(self):
        return self.Type

    def getPrice(self):
        return self.Price

    def setExecPrice(self, ExecPrice):
        self.ExecPrice = ExecPrice

    def getShares(self):
        return self.Shares


class Position:
        
    def __init__(self,Symbol):
        self.Symbol             = Symbol
        self.Pnl                = 0
        self.Shares             = 0
        self.AvgPrice           = 0
        self.TotalSharesTraded  = 0
        self.OpenOrders         = []
        self.ClosedOrders       = []
    
    def getSymbol(self):
        return self.Symbol

    def getPNL(self):
        return self.Pnl

    def getTotalSharesTraded(self):
        return self.TotalSharesTraded

    def getShares(self):
        return self.Shares

    def getAvgPrice(self):
        return     

    def calcAvgPrice(self, oldShares, oldPrice, newShares, newPrice):
        return (((abs(oldShares) * oldPrice) + (abs(newShares) * newPrice)) / (abs(oldShares) + abs(newShares)))
         
    def createOrder(self, Side, Type, Price, Shares):
        Symbol = self.getSymbol()
        theOrder = Order(Symbol, Side, Type, Price, Shares, )
        self.OpenOrders.append(theOrder)
        return theOrder

    def getTentPNL(self, current_price):
        if (self.Shares == 0):
            return 0
        elif (self.Shares < 0): 
            return (self.AvgPrice - current_price) * abs(self.Shares)
        elif (self.Shares > 0):
            return (current_price - self.AvgPrice) * abs(self.Shares)
        else:
            raise

    def checkOrders(self, bid, ask):
        for order in self.OpenOrders:
            if (order.getType() == "MARKET"):
                if (order.getSide() == "B"):
                    self.executeOrder(order, ask)
                elif (order.getSide() == "S"):
                    self.executeOrder(order, bid)
            elif (order.getType() == "LIMIT"):
                if (order.getSide() == "B" and ask <= order.getPrice()):
                    self.executeOrder(order, ask)
                elif (order.getSide == "S" and bid >= order.getPrice()):
                    self.executeOrder(order, bid)

    def executeOrder(self, order, price):
        if (order.getSide() == "B"):
            pnl = 0
            if (self.Shares < 0 and abs(self.Shares) > order.getShares()):
                pnl = (self.AvgPrice - price) * order.getShares()
            elif (self.Shares < 0 and abs(self.Shares) < order.getShares()):
                pnl = (self.AvgPrice - price) * abs(self.Shares)
                self.AvgPrice = price
            elif (self.Shares < 0 and abs(self.Shares) == order.getShares()):
                pnl = (self.AvgPrice - price) * order.getShares()
                self.AvgPrice = 0
            elif (self.Shares >= 0):
                self.AvgPrice = self.calcAvgPrice(self.getShares(), self.AvgPrice, order.getShares(), price)
            else:
                print "ERROR: Some condition occured that was not expected! (Buy Side)"
            self.Pnl += pnl
            self.Shares += order.getShares()	
        
        elif (order.getSide() == "S"):
            pnl = 0
            if (self.Shares > 0 and self.Shares > order.getShares()):
                pnl = (price - self.AvgPrice) * order.getShares()
            elif (self.Shares > 0 and self.Shares < order. getShares()):
                pnl = (price - self.AvgPrice) * self.Shares
                self.AvgPrice = price
            elif (self.Shares > 0 and abs(self.Shares) == order.getShares()):
                pnl = (price - self.AvgPrice) * order.getShares()
                self.AvgPrice = 0
            elif (self.Shares <= 0):
                self.AvgPrice = self.calcAvgPrice(self.getShares(), self.AvgPrice, order.getShares(), price)
            else:
                print "ERROR: Some condition occured that was not expected! (Sell Side)"
            self.Pnl += pnl
            self.Shares -= order.getShares()
        
        self.TotalSharesTraded += order.getShares()	
        order.setExecPrice(price)

        self.OpenOrders.remove(order)
        self.ClosedOrders.append(order)	

    def __str__(self):
        rstring = "Total position for" + self.Symbol + ":\n"
        rstring +=       "\tCurrent PNL: $" + str(round(self.Pnl,2))+"\n"
        rstring +=       "\tCurrent Position: " + str(self.Shares) + "\n"
        rstring +=       "\tTotal Shares Traded: " + str(self.TotalSharesTraded) + "\n"
        rstring +=       "\tOrders Open: " + str(len(self.OpenOrders)) + "\n"
        rstring +=       "\tOrders Closed: " + str(len(self.ClosedOrders)) + "\n"
        return rstring

