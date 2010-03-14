## Trade pairs
## Brian Giarrocco

import urllib2
import time
import csv
from position import Position

class TradePairs:
    def __init__(self, symbolA, symbolB, hedge_beta, trade_sd):
        self.pnl        = 0
        self.symbolA    = symbolA
        self.symbolB    = symbolB
        self.symAData   = SymbolData(symbolA)
        self.symBData   = SymbolData(symbolB)
        self.trade_sd   = float(trade_sd)
        self.hedge_beta = float(hedge_beta)
        self.spread     = self.generate_spread()
        self.returns    = []
        self.dates      = []

    def generate_spread(self):
        spread = []
        for i in range(len(self.symAData.symData)):
            date = self.symAData.symData[i][0]
            symAPrice   = self.symAData.symData[i][1]
            symBPrice   = self.symBData.symData[i][1]
            #print date,symAPrice,symBPrice
            diff = symAPrice - self.hedge_beta*symBPrice
            spread.append( (date, diff) )
            i+=1
        return spread

    def run_data(self):
        symAPosition = Position(self.symbolA)
        symBPosition = Position(self.symbolB)
        
        last_spread = 0
        date = None
        armedPlus   = False
        armedMinus  = False
        stop_trading= False
        totalDays   = 0
        lastTentPNL = 0
        ## Invest $50,000 In Pair A, and the apropriate numer of shares in B
        sharesA = int(50000/self.symAData.symData[0][1])
        sharesB = int(sharesA*self.hedge_beta)

        i=0

        for spread in self.spread:
            priceA  = self.symAData.symData[i][1]
            priceB  = self.symBData.symData[i][1]
            date    = self.symAData.symData[i][0]

            ## Test getin conditions
            if symAPosition.getShares() == 0 and spread[1] > self.trade_sd*2:
                armedPlus = True
            if symBPosition.getShares() == 0 and spread[1] < -self.trade_sd*2:
                armedMinus = True

            ##TODO: Add condition not to getin within 30 days of end of trading period
            if symAPosition.getShares() == 0 and armedPlus == True and spread[1] < self.trade_sd*2 and not stop_trading:
                ## Open Position
                print date,"|1","Short A (",symAPosition.getSymbol(),") / Buy B (",symBPosition.getSymbol(),")" 
                #print priceA,priceB
                ordA = symAPosition.createOrder("S","MARKET",priceA,sharesA)
                symAPosition.executeOrder(ordA, priceA)
                ordB = symBPosition.createOrder("B","MARKET",priceB,sharesB)
                symBPosition.executeOrder(ordB, priceB)
                armedPlus = False

            if symBPosition.getShares() == 0 and armedMinus == True and spread[1] < -self.trade_sd*2 and not stop_trading:
                ## Open Position
                print date,"|2","Buy A (",symAPosition.getSymbol(),") / Short B (",symBPosition.getSymbol(),")" 
                #print priceA,priceB
                ordA = symAPosition.createOrder("B","MARKET",priceA,sharesA)
                symAPosition.executeOrder(ordA, priceA)
                ordB = symBPosition.createOrder("S","MARKET",priceB,sharesB)
                symBPosition.executeOrder(ordB, priceB)
                armedMinus = False

            ## TODO: Add condition to getout if exceeds 3.5SD's, and stop trading that pair
            ## Test getout conditions
            if symAPosition.getShares() < 0 and (spread[1] < 0 or spread[1] > self.trade_sd*4):
                if (spread[1] > self.trade_sd*4):
                    stop_trading = True
                print date,"|3","Buy A (",symAPosition.getSymbol(),") / Sell B (",symBPosition.getSymbol(),")" 
                #print priceA,priceB
                ordA = symAPosition.createOrder("B","MARKET",priceA,sharesA)
                symAPosition.executeOrder(ordA, priceA)
                ordB = symBPosition.createOrder("S","MARKET",priceB,sharesB)
                symBPosition.executeOrder(ordB, priceB)

            if symAPosition.getShares() > 0 and (spread[1] > 0 or spread[1] < -self.trade_sd*4):
                if (spread[1] < -self.trade_sd*4):
                    stop_trading = True
                print date,"|4","Sell A (",symAPosition.getSymbol(),") / Buy B (",symBPosition.getSymbol(),")" 
                #print priceA,priceB
                ordA = symAPosition.createOrder("S","MARKET",priceA,sharesA)
                symAPosition.executeOrder(ordA, priceA)
                ordB = symBPosition.createOrder("B","MARKET",priceB,sharesB)
                symBPosition.executeOrder(ordB, priceB)


            ## If we have a position open, add it to total days.
            if symAPosition.getShares() != 0:
                totalDays += 1

            ## Add returns to dict for that day
            tentPNL = symAPosition.getPNL() + symBPosition.getPNL() + symAPosition.getTentPNL(priceA) + symBPosition.getTentPNL(priceB)
            self.returns.append(tentPNL - lastTentPNL)
            self.dates.append(date)
            lastTentPNL = tentPNL
            #print date,priceA,priceB,self.returns[-1]

            ## Update last_spread
            last_spread = spread[1]
            #print date,spread[0],spread[1]
            i+=1

        ## Unload positions at the end of trading
        if symAPosition.getShares() > 0:
            print date,"|","Sell A (",symAPosition.getSymbol(),") / Buy B (",symBPosition.getSymbol(),")" 
            #print priceA,priceB
            ordA = symAPosition.createOrder("S","MARKET",priceA,sharesA)
            symAPosition.executeOrder(ordA, priceA)
            ordB = symBPosition.createOrder("B","MARKET",priceB,sharesB)
            symBPosition.executeOrder(ordB, priceB)
        
        if symAPosition.getShares() < 0:
            print date,"|","Buy A (",symAPosition.getSymbol(),") / Sell B (",symBPosition.getSymbol(),")" 
            #print priceA,priceB
            ordA = symAPosition.createOrder("B","MARKET",priceA,sharesA)
            symAPosition.executeOrder(ordA, priceA)
            ordB = symBPosition.createOrder("S","MARKET",priceB,sharesB)
            symBPosition.executeOrder(ordB, priceB)

        print symAPosition
        print symBPosition
        totalPairPNL = symAPosition.getPNL() + symBPosition.getPNL()
        print "Positions open for:",totalDays,"days."
        print "Total Pair PNL:",totalPairPNL
        print 
        print
        return totalPairPNL,totalDays

class SymbolData:
    def __init__(self, symbol, startDate="2009-01-01", endDate="2010-02-16"):
        self.symbol     = symbol
        self.symData    = []
        self.startDate = time.strptime(startDate,"%Y-%m-%d")
        self.endDate = time.strptime(endDate,"%Y-%m-%d")
        self.retreive_daily_data()
        self.symData.reverse()

    def retreive_daily_data(self):
        ## Retreive the symbols data from yahoo_finance
        symFile = urllib2.urlopen("http://ichart.finance.yahoo.com/table.csv?s="+self.symbol+"&d=1&e=13&f=2010&g=d&a=0&b=5&c=1988&ignore=.csv")
        csv_parser = csv.reader(symFile)
        for row in csv_parser:
            if row[0] == "Date": continue
            date        = time.strptime(row[0],"%Y-%m-%d")
            adjClose    = row[6]
            if (date >= self.startDate and date < self.endDate):
                #print "Appending", date
                self.symData.append((row[0],float(adjClose)))
        

if __name__ == "__main__":
    pairs_file = csv.reader(open("pairs_list.csv"))
    totalPNL = 0
    totalDays = 0
    return_dict = {}
    for row in pairs_file:
        pairs_trade = TradePairs(row[0],row[1],row[2],row[3])
        pair_pnl,days_open = pairs_trade.run_data()
        identifier = row[0] + "-"+row[1]
        return_dict[identifier] = pairs_trade.returns
        dates                   = pairs_trade.dates
        totalPNL += pair_pnl
        totalDays += days_open

    output = open("output.csv","w")
    ## Create the return csv

    output.write(",")
    for date in dates:
        output.write(date+",")
    output.write("\n")

    for identifier, pair in return_dict.iteritems():

        output.write(identifier+",")
        for pnl in pair:
            output.write(str(pnl)+",")
        output.write("\n")




    print "You traded for",totalDays,"days."
    print "The total trading period, you made: $"+str(round(totalPNL,2))
    
   

