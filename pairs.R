## Brian Giarrocco
## Pairs Trading
## DSCI 495

## Many resources were used, in particular:
## http://www.quantmod.com/
## http://quanttrader.info/public/testForCoint.html
## http://go2.wordpress.com/?id=725X1342&site=sinamotamedi.wordpress.com&url=http%3A%2F%2Fdocs.google.com%2FDoc%3Fid%3Dd3kfhws_35g7p6hmff

## Declare the main function
main <- function(){
	## Use the quantmod package ( http://www.quantmod.com/ )
	library(quantmod)
	#library(tseries)

	## Create the symbols list, (Taken from google screener on utility stocks with an ADV > 500K [50 of them])
	the_symbols <- c("APWR","AYE","LNT","AEE","AEP","WTR","CPN","CNP","CMS","ED","CVA","D","DPL","DTE","DUK","EIX","EPB","ENI","ETR","EQT","EXC","FE","FPL","GXP","KMP","NI","NU","NRG","NST","NVE","OKE","POM","PCG","PNW","POR","PPL","PGN","PEG","RGNC","SCG","SRE","SUG","SE","TE","AES","SO","WR","WEC","XEL")
	#the_symbols <- c("AYE","CPN","AEP","DUK","LNT","DPL")

	## Retreive the symbols
	getSymbols(the_symbols)

	the_pairs <- combn(the_symbols, 2)
	## Loop to attempt to print out all pairs.
	i <- 1
	for (pair in the_pairs[1,]){
		#cat("Testing pair number",i,"\n")
		pval = DeterminePair(the_pairs[1,i],the_pairs[2,i])
		i <- i + 1
	}
}

## Declare DeterminePair Function
DeterminePair <- function(symAstring, symBstring) {
    ## Get the actual variables out of the string
    symA = get(symAstring)
    symB = get(symBstring)

    ## Tell it to only use the values for 2007 & 2008
    symA <- symA['2007::2008']
    symB <- symB['2007::2008']

    #cat("Comparing symbol",symAstring,"to",symBstring,"\n")
    
    symAClose = Ad(symA)
    symBClose = Ad(symB)

    ## Merge the two time series into t
    t.zoo = merge(symAClose, symBClose, all=FALSE)
    t <- as.data.frame(t.zoo)

    #cat("\t",length(symAClose),"\n")
	
    ## TODO: Find a better way to determine if full data is there.
    if (length(symAClose) != 504 || length(symBClose) != 504){
        #cat("\tAborting pair: Dont have full data on both \n")
        return("NULL")
    }
    
    #Create the linear model. According to "Paul Teetor" we should pin the intercept at 0,
    #becuase an intercept other than 0 would be hard to understand. If stock A's Price went to 0,
    #stock B's price should also.
    m <- lm(t[,1] ~ t[,2] + 0 , data=t)

    #print(m)
    ## Determine the beta coorelation (or hedge ratio)
    beta <- coef(m)[1]
    #cat("\tAssumed hedge ratio is", beta, "\n")

    ## Create the spread (StockA's Price - Beta*StockB's Price)
    sprd <- symAClose - beta*symBClose

    #ht <- adf.test(sprd, alternative="stationary", k=0)
    #cat("ADF p-value is", ht$p.value, "\n")
    ## Test spread using the PP test.
    pptest = PP.test(sprd)
    #cat("The P-value of the pair is:",pptest$p.value,"\n")
    if (pptest$p.value <= .01){
        #cat("Found Pair that meets threshold",symAstring,"vs.",symBstring," | P-Value:",pptest$p.value,"\n")
		cat(symAstring,",",symBstring,",",beta,",",sd(sprd),"\n", sep="")
	}
}

## Prints out some information about the pair, and returns the spread. Run this function
## after you determine which symbols are cointegrated.

ExaminePair <- function(symAstring, symBstring) {
	cat("Comparing symbol",symAstring,"to",symBstring,"\n")
	
	## Get the actual variables out of the string
    symA = get(symAstring)
    symB = get(symBstring)

    ## Tell it to only use the values for 2007 & 2008
    symA <- symA['2007::2008']
    symB <- symB['2007::2008']
	
	## Get the closing prices out of the stock objects
	symAClose = Ad(symA)
    symBClose = Ad(symB)

    ## Merge the two time series into t
    t.zoo = merge(symAClose, symBClose, all=FALSE)
    t <- as.data.frame(t.zoo)
	
	#Create the linear model. According to "Paul Teetor" we should pin the intercept at 0,
    #becuase an intercept other than 0 would be hard to understand. If stock A's Price went to 0,
    #stock B's price should also.
    m <- lm(t[,1] ~ t[,2] + 0 , data=t)

    print(m)
    ## Determine the beta coorelation (or hedge ratio)
    beta <- coef(m)[1]
    cat("Assumed hedge ratio is", beta, "\n")

    ## Create the spread (StockA's Price - Beta*StockB's Price)
    sprd <- symAClose - beta*symBClose
	
	cat("\n\nInformation on the Spread:\n")
	cat("The spreads mean:  ",mean(sprd),"\n")
	cat("The spreads stdev: ",sd(sprd),"\n")
	
    #ht <- adf.test(sprd, alternative="stationary", k=0)
    #cat("ADF p-value is", ht$p.value, "\n")
    ## Test spread using the PP test.
    pptest = PP.test(sprd)
	print(pptest)
	
	return(sprd)
}

## Start the main function
main()
