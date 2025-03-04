#include <stdio.h> 
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include "parson/parson.h"
#include "helpers.h"

#define MAX_LEN 100
#define MAX_MESSAGE 5000
#define MAX_LINE 400

// Function that returns id of a client command
int get_command_id (char command[15]) {
    if (strncmp(command, "register", 8) == 0) return 1;
    if (strncmp(command, "login", 5) == 0) return 2;
    if (strncmp(command, "enter_library", 13) == 0) return 3;
    if (strncmp(command, "get_books", 9) == 0) return 4;
    if (strncmp(command, "get_book", 8) == 0) return 5;
    if (strncmp(command, "add_book", 8) == 0) return 6;
    if (strncmp(command, "delete_book", 11) == 0) return 7;
    if (strncmp(command, "logout", 6) == 0) return 8;
    if (strncmp(command, "exit", 4) == 0) return 9;
    return 0;
}

// Function that returns a GET request message
char *get_request(char *host, char *url, char *cookies, char *headers) {
    char *message = calloc(MAX_MESSAGE, 1);
    char *line = calloc(MAX_LINE, 1);

    // Add GET line
    sprintf(line, "GET %s HTTP/1.1", url);
    compute_message(message, line);

    // Add HOST line
    memset(line, 0, MAX_LINE);
    sprintf(line, "HOST: %s", host);
    compute_message(message, line);

    // Add headers
    if (headers != NULL) {
        memset(line, 0, MAX_LINE);
        sprintf(line, "%s", headers);
        compute_message(message, line);
    }

    // Add cookies
    if (cookies != NULL) {
        memset(line, 0, MAX_LINE);
        sprintf(line, "%s", cookies);
        compute_message(message, line);
    }

    // Add final new line
    compute_message(message, "");

    free(line);
    return message;
}

// Function that returns a POST request message
char *post_request(char *host, char *url, char *content_type, 
                   char *body_data, char *cookies, char *headers) {
    char *message = calloc(MAX_MESSAGE, 1);
    char *line = calloc(MAX_LINE, 1);

    // Add POST line
    sprintf(line, "POST %s HTTP/1.1", url);
    compute_message(message, line);

    // Add HOST line
    memset(line, 0, MAX_LINE);
    sprintf(line, "HOST: %s", host);
    compute_message(message, line);

    // Add headers
    if (headers != NULL) {
        memset(line, 0, MAX_LINE);
        sprintf(line, "%s", headers);
        compute_message(message, line);
    }

    // Add content type
    memset(line, 0, MAX_LINE);
    sprintf(line, "Content-Type: %s", content_type);
    compute_message(message, line);

    // Add content length header
    memset(line, 0, MAX_LINE);
    sprintf(line, "Content-Length: %ld", strlen(body_data));
    compute_message(message, line);

     // Add cookies
    if (cookies != NULL) {
        memset(line, 0, MAX_LINE);
        sprintf(line, "%s", cookies);
        compute_message(message, line);
    }

    // Add new line to mark end of header
    compute_message(message, "");

    // Add data
    memset(line, 0, MAX_LINE);
    compute_message(message, body_data);

    free(line);
    return message;
}

// Function that returns a DELETE request message
char *delete_request(char *host, char *url, char *cookies, char *headers) {
    char *message = calloc(MAX_MESSAGE, 1);
    char *line = calloc(MAX_LINE, 1);

    // Add DELETE line
    sprintf(line, "DELETE %s HTTP/1.1", url);
    compute_message(message, line);

    // Add HOST line
    memset(line, 0, MAX_LINE);
    sprintf(line, "HOST: %s", host);
    compute_message(message, line);

    // Add headers
    if (headers != NULL) {
        memset(line, 0, MAX_LINE);
        sprintf(line, "%s", headers);
        compute_message(message, line);
    }

    // Add cookies
    if (cookies != NULL) {
        memset(line, 0, MAX_LINE);
        sprintf(line, "%s", cookies);
        compute_message(message, line);
    }

    // Add final new line
    compute_message(message, "");

    free(line);
    return message;
}

// Function that prints information of books from json received from server
void print_books (char *books_arr) {
    if (strcmp(books_arr, "[]") == 0) {
        printf("No books available.\n");
        return;
    }
    
    // Remove '[' and ']'
    char *books = calloc(strlen(books_arr), 1);
    memcpy(books, books_arr + 1, strlen(books_arr) - 2);
    
    // Get every book and display id and title
    char *tok = strtok(books, "{},");
    while (tok != NULL) {
        char *id = tok;
        tok = strtok(NULL, "{},");
        char *title = tok;
        tok = strtok(NULL, "{},");
        printf("Book information:\n");
        printf("\tId: %s\n", id + 5);        // print id, skip over "id"= part
        printf("\tTitle: %s\n", title + 8);  // print title, skip over "title"= part
    }
}

// Function that gets information from client about the book he wants to add
void get_book_information(char **title, char **author, char **publisher, 
                          char **genre, char **page_count) {
    char c;
    // Read title byte by byte
    write(1, "title=", 6);
    memset(*title, 0, MAX_LEN);
    int i = 0;
    read(0, &c, 1);
    while(c != '\n') {
        memcpy(*title + i, &c, 1);
        read(0, &c, 1);
        i++;
    }

    // Read author byte by byte
    write(1, "author=", 7);
    memset(*author, 0, MAX_LEN);
    i = 0;
    read(0, &c, 1);
    while(c != '\n') {
        memcpy(*author + i, &c, 1);
        read(0, &c, 1);
        i++;
    }

    // Read genre byte by byte
    write(1, "genre=", 6);
    memset(*genre, 0, MAX_LEN);
    i = 0;
    read(0, &c, 1);
    while(c != '\n') {
        memcpy(*genre + i, &c, 1);
        read(0, &c, 1);
        i++;
    }

    // Read publisher byte by byte
    write(1, "publisher=", 10);
    memset(*publisher, 0, MAX_LEN);
    i = 0;
    read(0, &c, 1);
    while(c != '\n') {
        memcpy(*publisher + i, &c, 1);
        read(0, &c, 1);
        i++;
    }

    // Read page count
    write(1, "page_count=", 11);
    memset(*page_count, 0, MAX_LEN);
    i = 0;
    read(0, &c, 1);
    while(c != '\n') {
        memcpy(*page_count + i, &c, 1);
        read(0, &c, 1);
        i++;
    }
}

// Create user information in json format (username and password)
char *user_information_json(char *username, char *password) {
    JSON_Value *msg_value = json_value_init_object();
    JSON_Object *msg_object = json_value_get_object(msg_value);
    json_object_set_string(msg_object, "username", username);
    json_object_set_string(msg_object, "password", password);
    char *info_json = calloc(MAX_LINE, 1);
    memcpy(info_json, json_serialize_to_string(msg_value), strlen(json_serialize_to_string(msg_value)));
    return info_json;
}

// Print information about a book from json object
void print_book(JSON_Object *book_object) {
    printf("Book information:\n");
    printf("\tTitle: \"%s\"\n", json_object_get_string(book_object, "title"));
    printf("\tAuthor: %s\n", json_object_get_string(book_object, "author"));
    printf("\tPublisher: %s\n", json_object_get_string(book_object, "publisher"));
    printf("\tGenre: %s\n", json_object_get_string(book_object, "genre"));
    printf("\tPage count: %d\n", (int)json_object_get_number(book_object, "page_count"));
}

int main()
{
    // Server information
    char host_ip[16] = "34.118.48.238";
    int portno = 8080;
    int sockfd;

    char *authentification_cookie = NULL;
    char *authorization_header = NULL;

    char command[15];
    while (1) {
        // Read command and get id
        scanf("%s", command);
        int command_id = get_command_id(command);
        
        switch(command_id) {
            case 1: {
                // Register command
                // Get username
                char username[MAX_LEN];
                printf("username=");
                scanf("%s", username);

                // Get password
                char password[MAX_LEN];
                printf("password=");
                scanf("%s", password);

                // Create json object with username and password and send POST request
                char *json_string = user_information_json(username, password);
                sockfd = open_connection(host_ip, portno, AF_INET, SOCK_STREAM, 0);
                char *message = post_request(host_ip, "/api/v1/tema/auth/register",
                                             "application/json", json_string,
                                             NULL, NULL);
                send_to_server(sockfd, message);

                // Receive response from server and get json object
                char *response = receive_from_server(sockfd);
                JSON_Value *resp_value = json_parse_string(basic_extract_json_response(response));
                JSON_Object *resp_object = json_value_get_object(resp_value);
                if (json_object_get_string(resp_object, "error") == NULL) {
                    // If object has no error field, everything is ok
                    printf("User %s created successfully.\n", username);
                } else {
                    // Otherwise, print error
                    printf("Error: %s\n", json_object_get_string(resp_object, "error"));
                }
                
                if (message != NULL) free(message);
                close_connection(sockfd);
                break;
            }
            case 2: {
                // Login command
                // Get username
                char username[MAX_LEN];
                printf("username=");
                scanf("%s", username);

                // Get password
                char password[MAX_LEN];
                printf("password=");
                scanf("%s", password);

                // Create json object with username and password and send POST request
                char *json_string = user_information_json(username, password);
                sockfd = open_connection(host_ip, portno, AF_INET, SOCK_STREAM, 0);
                char *message = post_request(host_ip, "/api/v1/tema/auth/login",
                                             "application/json", json_string,
                                              NULL, NULL);
                send_to_server(sockfd, message);
                
                // Receive response from server and get json object
                char *response = receive_from_server(sockfd);
                JSON_Value *resp_value = json_parse_string(basic_extract_json_response(response));
                JSON_Object *resp_object = json_value_get_object(resp_value);
                if (json_object_get_string(resp_object, "error") == NULL) {
                    // If object has no error field, everything is ok
                    printf("User %s logged in successfully.\n", username);

                    // Extract cookie
                    char *cookie_line = strstr(response, "Cookie:");
                    char *cookie_line_end = strchr(cookie_line, ';');
                    cookie_line_end[0] = '\0';
                    
                    // Copy cookie line
                    authentification_cookie = calloc(MAX_LEN, 1);
                    memcpy(authentification_cookie, cookie_line, strlen(cookie_line));
                } else {
                    // Otherwise, print error
                    printf("Error: %s\n", json_object_get_string(resp_object, "error"));
                }

                if (message != NULL) free(message);
                close_connection(sockfd);
                break;
            }
            case 3: {
                // Enter_library command
                // Send GET request to server with authentification cookie
                sockfd = open_connection(host_ip, portno, AF_INET, SOCK_STREAM, 0);
                char *message = get_request(host_ip, "/api/v1/tema/library/access",
                                            authentification_cookie, NULL);
                send_to_server(sockfd, message);

                // Receive response from server and get json object
                char *response = receive_from_server(sockfd);
                JSON_Value *resp_value = json_parse_string(basic_extract_json_response(response));
                JSON_Object *resp_object = json_value_get_object(resp_value);
                if (json_object_get_string(resp_object, "error") == NULL) {
                    // If object has no error field, everything is ok
                    printf("Access granted.\n");

                    // Get JWT token and create Authorization header
                    authorization_header = calloc(MAX_LEN, 1);
                    memcpy(authorization_header, "Authorization: Bearer ", 22);
                    memcpy(authorization_header + 22, 
                           json_object_get_string(resp_object, "token"),
                           strlen(json_object_get_string(resp_object, "token")) + 1);
                } else {
                    // Otherwise, print error
                    printf("Error: %s\n", json_object_get_string(resp_object, "error"));
                }

                if (message != NULL) free(message);
                close_connection(sockfd);
                break;
            }
            case 4: {
                // Get_books command
                // Send GET request to server with authorization header 
                sockfd = open_connection(host_ip, portno, AF_INET, SOCK_STREAM, 0);
                char *message = get_request(host_ip, "/api/v1/tema/library/books",
                                            NULL, authorization_header);
                send_to_server(sockfd, message);

                // Receive response from server and get json object
                char *response = receive_from_server(sockfd);
                JSON_Value *resp_value = json_parse_string(basic_extract_json_response(response));
                JSON_Object *resp_object = json_value_get_object(resp_value);
                if (json_object_get_string(resp_object, "error") == NULL) {
                    // If object has no error field, everything is ok
                    // Get books array and print it
                    char *books = strchr(response, '[');
                    print_books(books);
                } else {
                    // Otherwise, print error
                    printf("Error: %s\n", json_object_get_string(resp_object, "error"));
                }
                
                if (message != NULL) free(message);
                close_connection(sockfd);
                break;
            }
            case 5: {
                // Get_book command
                // Get book id and complete URL
                char id[MAX_LEN];
                printf("id=");
                scanf("%s", id);
                char url[MAX_LEN];
                sprintf(url, "/api/v1/tema/library/books/%s", id);

                // Send GET request to server with authorization header
                sockfd = open_connection(host_ip, portno, AF_INET, SOCK_STREAM, 0);
                char *message = get_request(host_ip, url, NULL, authorization_header);
                send_to_server(sockfd, message);

                // Receive response from server and get json object
                char *response = receive_from_server(sockfd);
                JSON_Value *resp_value = json_parse_string(basic_extract_json_response(response));
                JSON_Object *resp_object = json_value_get_object(resp_value);
                if (json_object_get_string(resp_object, "error") == NULL) {
                    // If object has no error field, everything is ok
                    // Parse object and print book information
                    response = strchr(response, '{');
                    response[strlen(response)] = '\0';
                    JSON_Value *book_value = json_parse_string(response);
                    JSON_Object *book_object = json_value_get_object(book_value);
                    print_book(book_object);
                } else {
                    // Otherwise, print error
                    printf("Error: %s\n", json_object_get_string(resp_object, "error"));
                }

                if (message != NULL) free(message);
                close_connection(sockfd);
                break;
            }
            case 6: {
                // Add_book command
                // Get book information
                char *title = calloc(MAX_LEN, 1);
                char *author = calloc(MAX_LEN, 1);
                char *genre = calloc(MAX_LEN, 1);
                char *publisher = calloc(MAX_LEN, 1);
                char *page_count = calloc(MAX_LEN, 1);
                get_book_information(&title, &author, &publisher, &genre, &page_count);

                // Otherwise, create json object
                JSON_Value *msg_value = json_value_init_object();
                JSON_Object *msg_object = json_value_get_object(msg_value);
                json_object_set_string(msg_object, "title", title);
                json_object_set_string(msg_object, "author", author);
                json_object_set_string(msg_object, "genre", genre);
                json_object_set_string(msg_object, "page_count", page_count);
                json_object_set_string(msg_object, "publisher", publisher);
                char *json_string = json_serialize_to_string(msg_value);

                // Send POST request to server with authorization header and
                // book information
                sockfd = open_connection(host_ip, portno, AF_INET, SOCK_STREAM, 0);
                char *message = post_request(host_ip, "/api/v1/tema/library/books",
                                             "application/json", json_string,
                                             NULL, authorization_header);
                send_to_server(sockfd, message);

                // Receive response from server and get json object
                char *response = receive_from_server(sockfd);
                JSON_Value *resp_value = json_parse_string(strchr(response, '{'));
                JSON_Object *resp_object = json_value_get_object(resp_value);
                if (json_object_get_string(resp_object, "error") == NULL) {
                    // If object has no error field, everything is ok
                    printf("Book added successfully.\n");
                } else {
                    // Otherwise, print error
                    printf("Error: %s\n", json_object_get_string(resp_object, "error"));
                }
                
                // Close connection
                if (message != NULL) free(message);
                if (title != NULL) free(title);
                if (author != NULL) free(author);
                if (genre != NULL) free(genre);
                if (publisher != NULL) free(publisher);
                if (page_count != NULL) free(page_count);
                close_connection(sockfd);
                break;
            }
            case 7: {
                // Delete book command
                // Get book id
                char id[MAX_LEN];
                printf("id=");
                scanf("%s", id);
                char url[MAX_LEN];
                sprintf(url, "/api/v1/tema/library/books/%s", id);

                // Send DELETE request to server with authorization header
                sockfd = open_connection(host_ip, portno, AF_INET, SOCK_STREAM, 0);
                char *message = delete_request(host_ip, url, NULL, authorization_header);
                send_to_server(sockfd, message);

                // Receive response from server and get json object
                char *response = receive_from_server(sockfd);
                JSON_Value *resp_value = json_parse_string(basic_extract_json_response(response));
                JSON_Object *resp_object = json_value_get_object(resp_value);
                if (json_object_get_string(resp_object, "error") == NULL) {
                    // If object has no error field, everything is ok
                    printf("Book deleted successfully.\n");
                } else {
                    // Otherwise, print error
                    printf("Error: %s\n", json_object_get_string(resp_object, "error"));
                }

                if (message != NULL) free(message);
                close_connection(sockfd);
                break;
            }
            case 8: {
                // Logout command
                // Send GET request to server with authentification cookie
                sockfd = open_connection(host_ip, portno, AF_INET, SOCK_STREAM, 0);
                char *message = get_request(host_ip, "/api/v1/tema/auth/logout",
                                            authentification_cookie, NULL);
                send_to_server(sockfd, message);

                // Receive response from server and get json object
                char *response = receive_from_server(sockfd);
                JSON_Value *resp_value = json_parse_string(basic_extract_json_response(response));
                JSON_Object *resp_object = json_value_get_object(resp_value);
                if (json_object_get_string(resp_object, "error") == NULL) {
                    // If object has no error field, everything is ok
                    printf("Log out successful.\n");
                    memset(authentification_cookie, 0, MAX_LEN);
                    memset(authorization_header, 0, MAX_LEN);
                } else {
                    // Otherwise, print error
                    printf("Error: %s\n", json_object_get_string(resp_object, "error"));
                }

                if (message != NULL) free(message);
                close_connection(sockfd);
                break;
            }
            case 9: {
                // Exit command
                // Free memory
                if (authorization_header != NULL) free(authorization_header);
                if (authentification_cookie != NULL) free(authentification_cookie);
                return 0;
            }
            default: {
                // Wrong command
                printf("Wrong command.\n");
                break;
            }
        }
    }
    return 0;
}