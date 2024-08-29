![image](https://github.com/user-attachments/assets/4b47db38-50c0-4284-8ba7-12bdf193baa7)

# HennaStoreApp

## Description

Welcome to HennaStoreApp! This Django-based e-commerce platform is dedicated to showcasing and selling traditional Palestinian cultural dresses. Our app is designed to offer a seamless shopping experience, allowing users to explore a rich catalog of dresses, make purchases, and engage with Palestinian heritage through fashion.

With a focus on user experience and cultural appreciation, HennaStoreApp provides a comprehensive range of features for both customers and administrators, ensuring efficient management and an engaging shopping experience.

## Features

### 1. Product Listings
- **Catalog of Dresses:** Browse a collection of traditional Palestinian dresses with detailed images, descriptions, and pricing information.

### 2. User Authentication
- **Account Management:** Users can register, log in, and manage their personal accounts.

### 3. Shopping Cart
- **Cart Functionality:** Add items to the cart, select sizes, and proceed to checkout with ease.

### 4. Order Management
- **Order Tracking:** View order history and track the status of purchases.

### 5. Admin Dashboard
- **Product Management:** Admins can manage product listings, including adding and updating dresses.
- **User Management:** Admins can handle user accounts and permissions.
- **Order Management:** Track and manage customer orders and their statuses.

## Technical Details

### Front-End Technologies

![HTML](https://github.com/user-attachments/assets/cac34e15-2550-4abc-ac61-c7e1e71e5656) HTML: Structure and content of the web pages.<br>
![CSS](https://github.com/user-attachments/assets/dce32069-f225-4427-ae60-9a16162af91e) CSS: Styling and visual presentation.<br>
![JavaScript](https://github.com/user-attachments/assets/82c158f7-c636-4bac-a6d7-9fdfcb3e3a18) JavaScript: Interactive elements and dynamic content.<br>
![Bootstrap](https://github.com/user-attachments/assets/a8467c20-50e8-421c-9eca-ac6a2d179005) Bootstrap: Responsive design and UI components.<br>

### Back-End Technologies

![Python](https://github.com/user-attachments/assets/c6902435-515e-405b-9fa0-c5d5ab98a6a4) Python: Back-end code.<br>
![Django](https://github.com/user-attachments/assets/8769dfb5-d412-4990-ac28-e0162a851cc5) Django: Framework for building the server-side application.<br>
![API](https://github.com/user-attachments/assets/9721ad16-4d57-4c14-9d14-070b3245ff7e) API: Interface for communication between front-end and back-end.<br>
![AJAX](https://github.com/user-attachments/assets/ee29eef2-04e6-42af-8510-db57cee43f85) AJAX: Asynchronous requests for dynamic content updates.<br>

## Models

### 1. Dress
- **Description:** Represents dresses available for sale.
- **Fields:** Name, description, price, images.

### 2. User
- **Description:** Manages user information and authentication.

### 3. Order
- **Description:** Manages user orders, including status and total amount.

### 4. Category
- **Description:** Categorizes dresses into different types for easier browsing.

## Deployment

- **Web Server:** Nginx (configured to serve the Django application).
- **Database Management:** PostgreSQL, with recent adjustments made to the database configuration.
- **Error Handling:** Includes handling for database connection issues and missing tables.

## Recent Updates

- **Database Migration:** Transitioned from SQLite to PostgreSQL for better performance and scalability.
- **Feature Expansion:** Added functionality for managing product sizes and enhanced search features.

## Challenges and Solutions

- **Database Migration:** Required updates to database configuration and handling migration issues.
- **Nginx Configuration:** Resolved port binding conflicts and ensured proper server setup.

## Future Plans

- **Feature Expansion:** Plans to introduce men’s traditional clothes and broaden the product range.
- **Enhanced User Experience:** Ongoing improvements to the user interface and additional functionalities based on feedback.

If you have any specific questions or need assistance with particular features or issues related to HennaStoreApp, feel free to ask!
