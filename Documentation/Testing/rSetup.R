main <- function(){
    return( collection )
}

setup <- function(){
    collection <<- (1)

    for( i in 2:4568782 ){
        if( 4568782%%i == 0){
            collection <- c( collection, i )
        }
    }

    return( collection )
}

paste0( "Begining" )
start.time <- Sys.time()
setup()
main()
end.time <- Sys.time()
time.taken <- end.time - start.time
time.taken
paste0( "End" )