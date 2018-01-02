
#test_service
#Test service definition script for AnalyticsServer deployment.

#-------------
#Declare libraries
library(MASS)
library(RJSONIO)

#-------------
#Pre-load data
df <- iris


#Required main() function body

main <- function(input){

        x <- fromJSON(input)
        
        n <- length(x$Individuals)
        name = character(n)
        age = numeric(n)
        BMI = numeric(n)
        output = list()

        for (i in 1:n){
                k <- x$Individuals[[i]]
                print(difftime(as.Date(k$DOB,"%d-%b-%Y"), Sys.Date(),unit="weeks"))
                name[i] <- k$Name
                age[i] <- as.numeric(difftime(Sys.Date(), as.Date(k$DOB,"%d-%b-%Y"),unit="weeks"))/52.25
                BMI[i] <- k$Weight/((k$Height/100)^2)
                output[[i]] <- list(Name=name[i],Age=age[i],BMI=BMI[i])
        }

        out <- list()
        out$correlationID = x$correlationID
        out$BMI = output


        ret_payload <- toJSON(out)

	
	return(ret_payload)
}









