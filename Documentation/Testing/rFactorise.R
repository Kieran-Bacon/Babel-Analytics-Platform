main <- function( number ){

    collection <- (1)

    for( i in 2:number ){
        if( number%%i == 0){
            collection <- c( collection, i )
        }
    }

    return( collection )
}

value <- 96724316

paste0( "Begining" )
start.time <- Sys.time()
main(value)
end.time <- Sys.time()
time.taken <- end.time - start.time
time.taken
paste0( "End" )