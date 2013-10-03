#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>


#define MYPORT "17"  // the port users will be connecting to
#define BACKLOG 10    // how many pending connections queue will hold

int main(int argc, char **argv)
{
   if (argc!=2)
   {
      printf("Usage: %s message\n", argv[0]);
      return 1;
   }
   
   struct sockaddr_storage their_addr;
   socklen_t addr_size;
   struct addrinfo hints, *res;
   int sockfd, new_fd;

   memset(&hints, 0, sizeof hints);
   hints.ai_family = AF_UNSPEC;  // use IPv4 or IPv6, whichever
   hints.ai_socktype = SOCK_STREAM;
   hints.ai_flags = AI_PASSIVE;    // fill in my IP for me

   getaddrinfo(NULL, MYPORT, &hints, &res);

   // make a socket, bind it, and listen on it:

   sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
   if (bind(sockfd, res->ai_addr, res->ai_addrlen) != 0)
   {
      perror("Bind failed");
      exit(1);
   }
   
   if (listen(sockfd, BACKLOG) != 0)
   {
      perror("Listen failed");
      exit(1);
   }
   
   
   // now accept an incoming connection:

   addr_size = sizeof their_addr;
   while ((new_fd = accept(sockfd, (struct sockaddr *)&their_addr, &addr_size))>-1){
      send(new_fd, argv[1], strlen(argv[1]), 0);
      send(new_fd, "\n", strlen("\n"), 0);
      close(new_fd);
   }
}


