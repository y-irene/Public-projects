#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netinet/tcp.h>
#include "helpers.h"
#include <math.h>

// Auxiliary functions

// Search a subscriber by its id
struct subscriber *search_by_id (struct subscriber *subscribers, int n, 
	char *id) {
	struct subscriber *found = NULL;
	for (int i = 0; i < n; i++) {
		if (strncmp(subscribers[i].id, id, strlen(id)) == 0) {
			found = &(subscribers[i]);
			break;
		}
	}
	return found;
}

// Search a subscriber by its socket
struct subscriber *search_by_sockfd (struct subscriber *subscribers, int n, 
	int sockfd) {
	struct subscriber *found = NULL;
	for (int i = 0; i < n; i++) {
		if (subscribers[i].sockfd == sockfd) {
			found = &(subscribers[i]);
			break;
		}
	}
	return found;
}

// Function that tries to add a new subscriber to the array of subscribers
// Returns 0 if a new subscriber has been added, 1 if a subscrier tries to sign
// in with a taken id and 2 if tre subscriber is reconnecting
int add_new_subscriber (struct subscriber **subscribers, int *n, char *id, 
	int sockfd) {
	struct subscriber *new = search_by_id(*subscribers, *n, id);

	if (new == NULL) {
		// If the subscriber isn't already in the array of subscribers, add it
		struct subscriber *aux = (struct subscriber *)realloc(*subscribers, 
			(*n + 1) * sizeof(struct subscriber));
		DIE(aux == NULL, "Server error: Realloc failed");

		strcpy(aux[*n].id, id);
		aux[*n].sockfd = sockfd;
		aux[*n].connected = 1;
		aux[*n].subscriptions = NULL;
		aux[*n].subscriptions_num = 0;

		*subscribers = aux;
		*n = *n + 1;
		return 0;
	} else {
		// If a subscriber with the same id is in the array of subscribers
		if (new->connected == 1) {
			// If the subscriber with the same id is connected, reject the 
			// subscriber that is trying to sign in
			close(sockfd);
			printf("Client %s already connected.\n", new->id);
			return 1;
		} else {
			// If the subscriber with the same id is not connected, the 
			// subsriber reconnected so change its sockfd and send unsent 
			// messsages
			new->sockfd = sockfd;
			new->connected = 1;

			for (int i = 0; i < new->subscriptions_num; i++) {
				for (int j = 0; j < new->subscriptions[i].unsent_msg_num; j++) {
					int rs = send(new->sockfd, &new->subscriptions[i].unsent_msg[j], 
						sizeof(struct udp_msg), 0);
					DIE(rs < 0, "Server error: Send UDP message");
				}
				free(new->subscriptions[i].unsent_msg);
				new->subscriptions[i].unsent_msg_num = 0;
			}
			return 2;
		}
	}
}

// Function that subscribes a subsciber to a topic identified by its name
void subscribe (struct subscriber *s, char *topic, int sf) {
	struct subscription *aux = realloc(s->subscriptions, 
		(s->subscriptions_num + 1) * sizeof(struct subscription));
	DIE(aux == NULL, "Server error: Realloc failed");

	// Create the new subscription
	aux[s->subscriptions_num].sf = sf;
	strcpy(aux[s->subscriptions_num].topic, topic);
	aux[s->subscriptions_num].unsent_msg_num = 0;
	aux[s->subscriptions_num].unsent_msg = NULL;

	s->subscriptions = aux;
	s->subscriptions_num = s->subscriptions_num + 1;
}

// Function that unsubscribes a subsciber from a topic identified by its name
void unsubscribe (struct subscriber *s, char *topic) {
	for (int i = 0; i < s->subscriptions_num; i++) {
		if(strcmp(s->subscriptions[i].topic, topic) == 0) {
			// If subscription's topic matches the topic, remove it
			memcpy(s->subscriptions + i, 
				s->subscriptions + s->subscriptions_num - 1, 
				sizeof(struct subscription));
			struct subscription *aux = realloc(s->subscriptions, 
				(s->subscriptions_num - 1) * sizeof(struct subscription));

			s->subscriptions = aux;
			s->subscriptions_num = s->subscriptions_num - 1;
			break;
		}
	}
}

// Function that creates an udp message from a buffer
struct udp_msg *parse_udp (char *buffer, unsigned int bufflen, 
	struct sockaddr_in udp_client) {
	// Get port and ip of UDP client
	int port = ntohs(udp_client.sin_port);
	char *ip = inet_ntoa(udp_client.sin_addr);

	// Get topic from message sent by UDP client
	char topic[51];
	memset(topic, 0, 51);
	memcpy(topic, buffer, 50);

	// Get data_type from message sent by UDP client
	unsigned char data_type = *(buffer + 50);
	
	// Get value and convert it into string
	char *value = calloc(1, 1501);
	DIE (value == NULL, "Server error: Calloc failed");
	
	if (data_type == 0 ) {
		// If payload is int
		unsigned char sign = *(buffer + 51);
		uint32_t abs_number = ntohl(*((uint32_t *)(buffer + 52)));
		int number = abs_number;
		if (sign == 1) {
			number = number * (-1);
		}
		sprintf(value, "%d", number);
	} else if (data_type == 1) {
		// If payload is short real
		uint16_t abs_number = ntohs(*((uint16_t *)(buffer + 51)));
		float number = abs_number / 100.0;
		sprintf(value, "%.2f", number);
	} else if (data_type == 2) {
		// If payload is float
		unsigned char sign = *(buffer + 51);
		uint32_t abs_number = ntohl(*((uint32_t *)(buffer + 52)));
		uint8_t pwr = *(uint8_t *)(buffer + 56);

		float number = abs_number * pow(10, pwr * (-1));
		if (sign == 1) {
			number = number * (-1);
		}
		sprintf(value, "%.*f", pwr, number);
	} else if (data_type == 3) {
		// If payload is string
		memcpy(value, buffer + 51, bufflen - 51);
	}

	// Alloc a new UDP message and add information
	struct udp_msg *m = calloc(1, sizeof(struct udp_msg));
	DIE(m == NULL, "Server error: Calloc failed");

	memcpy(m->ip, ip, strlen(ip));
	m->port_udp = port;
	memcpy(m->topic, topic, strlen(topic));
	m->data_type = data_type;
	memcpy(m->payload, value, strlen(value));
	free(value);
	return m;
}

// Function that send an UDP message to all active subscribers
void send_udp (struct subscriber *subscribers, int n, struct udp_msg *m) {
	// For each subscriber, check the subscription list to see if the current
	// message should reach them
	for (int k = 0; k < n; k++) {
		struct subscription *found = NULL;
		struct subscriber *subscriber = &subscribers[k];
		
		// Search subscription by topic
		for (int j = 0; j < subscribers[k].subscriptions_num; j++){
			if(strcmp(m->topic, subscribers[k].subscriptions[j].topic) == 0){
				// If subscription is found
				found = &subscribers[k].subscriptions[j];
				if (subscriber->connected == 1) {
					// If client si connected, send the message
					int rs = send(subscriber->sockfd, m, sizeof(struct udp_msg), 0);
					DIE(rs < 0, "Server error: Send UDP message");
				} else {
					if (found->sf == 1) {
						// If client is disconnected and sf is activated, 
						// store the message to send it later
						struct udp_msg *aux = realloc(found->unsent_msg, 
							(found->unsent_msg_num + 1) * sizeof(struct udp_msg));
						DIE(aux == NULL, "Server error: Realloc failed");

						memcpy(&aux[found->unsent_msg_num], m, sizeof(struct udp_msg));
						found->unsent_msg = aux;
						found->unsent_msg_num = found->unsent_msg_num + 1;
					}
				}
				break;
			}
		}
	}
}

int main (int argc, char *argv[]) {
	setvbuf(stdout, NULL, _IONBF, BUFSIZ);
	int enable = 1;

	// Check number of arguments
	DIE(argc < 2, "Server error: Too few arguments");

	// Port number
	int port_num = atoi(argv[1]);
	DIE(port_num > 65535, "Server error: Port number too big");
	DIE(port_num < 1024, "Server error: Port number too small");

	// Server address
	struct sockaddr_in server_addr;
	memset((char *)(&server_addr), 0, sizeof(server_addr));
	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(port_num);
	server_addr.sin_addr.s_addr = INADDR_ANY;

	// UDP socket
	int udp_sockfd = socket(AF_INET, SOCK_DGRAM, 0);
	DIE(udp_sockfd < 0, "Server error: UDP socket");
	int rs = bind(udp_sockfd, (struct sockaddr *)(&server_addr), 
		sizeof(struct sockaddr));
	DIE(rs < 0, "Server error: UDP bind");
	if (setsockopt(udp_sockfd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) == -1) {
	  perror("setsocketopt");
	  exit(1);
	}

	memset((char *)(&server_addr), 0, sizeof(server_addr));
	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(port_num);
	server_addr.sin_addr.s_addr = INADDR_ANY;

	// TCP socket
	int tcp_sockfd = socket(AF_INET, SOCK_STREAM, 0);
	DIE(tcp_sockfd < 0, "Server error: TCP socket");
	rs = bind(tcp_sockfd, (struct sockaddr *)(&server_addr), sizeof(struct sockaddr));
	DIE(rs < 0, "Server error: TCP bind");
	if (setsockopt(tcp_sockfd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) == -1) {
	  perror("setsocketopt");
	  exit(1);
	}
	// Disable Neagle's algorithm
	if (setsockopt(tcp_sockfd, IPPROTO_TCP, TCP_NODELAY, &enable, sizeof(int)) == -1) {
		perror("setsocketopt");
		exit(1);
	}

	// Listen on TCP socket
	rs = listen(tcp_sockfd, MAX_CLIENTS);
	DIE(rs < 0, "Server error: Listen");

	// Sockfd set
	fd_set read_fds, tmp_fds;
	int fdmax;
	FD_ZERO(&read_fds);
	FD_ZERO(&tmp_fds);
	FD_SET(tcp_sockfd, &read_fds);      // add TCP
	FD_SET(udp_sockfd, &read_fds);      // add UDP
	fdmax = (tcp_sockfd < udp_sockfd) ? udp_sockfd : tcp_sockfd;
	FD_SET(STDIN_FILENO, &read_fds);    // add STDIN
	fdmax = (fdmax < STDIN_FILENO) ? STDIN_FILENO : fdmax;

	// Subscribers array
	struct subscriber *subscribers = NULL;
	int tcp_num = 0;

	int n, i;

	// Subscriber message auxiliary variables
	unsigned int tcp_msg_len = sizeof(struct subscriber_msg);
	char tcp_msg[tcp_msg_len];

	while(1) {
		tmp_fds = read_fds;

		// Select a socket
		rs = select(fdmax + 1, &tmp_fds, NULL, NULL, NULL);
		DIE(rs < 0, "Server error: Select");

		for (i = 0; i <= fdmax; i++) {
			if (FD_ISSET(i, &tmp_fds)) {
				if (i == STDIN_FILENO) {
					// If STDIN socket is set, read server input
					char command[10];
					memset(command, 0, 10);
					fgets(command, 9, stdin);
					
					if (strncmp(command, "exit", 4) == 0) {
						// Close sockets
						close(udp_sockfd);
						close(tcp_sockfd);

						for (int j = 0; j <= fdmax; j++)
							if (FD_ISSET(j, &read_fds))
								close(j);

						// Free memory
						for (int j = 0; j < tcp_num; j++) {
							for (int k = 0; k < subscribers[j].subscriptions_num; k++) {
								if (subscribers[j].subscriptions[k].unsent_msg != NULL) {
									free(subscribers[j].subscriptions[k].unsent_msg);
								}
							}
							free(subscribers[j].subscriptions);
						}
						free(subscribers);
						return 0;
					} else {
						fprintf(stderr, "Server error: Invalid command.");
					}
				} else if (i == tcp_sockfd) {
					// If TCP socket is set, it is a new connection request
					// Accept connection
					struct sockaddr_in tcp_addr;
					unsigned int tcp_addr_len = sizeof(tcp_addr);
					int new_sockfd = accept(i, (struct sockaddr *)(&tcp_addr), 
											&tcp_addr_len);
					DIE(new_sockfd < 0, "Server error: Accept");

					// Disable Neagle's algorithm
					if (setsockopt(new_sockfd, IPPROTO_TCP, TCP_NODELAY, 
						&enable, sizeof(int)) == -1) {
						perror("setsocketopt");
						exit(1);
					}

					// Get id from TCP client
					memset(tcp_msg, 0, tcp_msg_len);
					for (int current_byte = 0; current_byte < tcp_msg_len; current_byte++) {
						n = recv(new_sockfd, tcp_msg + current_byte, 1, 0);
						DIE(n < 0, "Server: ID receive error");
					}
					
					// Add subscriber to subscribers array
					struct subscriber_msg *m = (struct subscriber_msg *)tcp_msg;
					char *id = m->payload;
					n = add_new_subscriber(&subscribers, &tcp_num, id, 
											new_sockfd);
					
					if (n != 1) {
						// If connection is accepted, add sockfd to set 
						// and print message
						FD_SET(new_sockfd, &read_fds);
						fdmax = (fdmax < new_sockfd) ? new_sockfd : fdmax;

						int port = ntohs(tcp_addr.sin_port);
						struct in_addr ip = tcp_addr.sin_addr;
						printf("New client %s connected from %s:%d.\n", id, 
							inet_ntoa(ip), port);
					}
				} else if (i == udp_sockfd) {
					// If UDP socket is set, receive UDP message
					struct sockaddr_in udp_client;
					socklen_t udp_len = sizeof(udp_client);
					
					char buffer[1551];
					memset(buffer, 0, 1551);
					int bufflen = 1551;
					n = recvfrom(udp_sockfd, buffer, bufflen, 0, 
						(struct sockaddr *)(&udp_client), &udp_len);
					DIE(n < 0, "Server error: UDP message recv");

					struct udp_msg *msg = parse_udp(buffer, bufflen, udp_client);
					send_udp(subscribers, tcp_num, msg);
					free(msg);
				} else {
					// A TCP client socket is set, so receive message
					struct subscriber *found = search_by_sockfd(subscribers, 
											   tcp_num, i);
											   
					memset(tcp_msg, 0, tcp_msg_len);
					n = recv(i, tcp_msg, 1, 0);
					DIE(n < 0, "Server error: TCP message receive");

					if (n == 0) {
						// Client disconnected
						found->connected = 0;
						found->sockfd = -1;
						printf("Client %s disconnected.\n", found->id);
						close(i);
						FD_CLR(i, &read_fds);
					} else {
						// Subscribe/Unsubscribe request, read the rest of message
						for (int current_byte = 1; current_byte < tcp_msg_len; current_byte++) {
							n = recv(i, tcp_msg + current_byte, 1, 0);
							DIE(n < 0, "Server error: TCP message receive");
						}
						struct subscriber_msg *m = (struct subscriber_msg *)tcp_msg;
						if (m->type == 1) {
							// If message type is 1, it is a subscribe request
							subscribe(found, m->payload, m->sf);
						} else  {
							// If message type is 2, it is an unsubscribe request
							unsubscribe(found, m->payload);
						}
					}
				}
			}
		}
	}
	return 0;
}