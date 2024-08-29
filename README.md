HennaStoreApp is a Django-based project designed to showcase and sell Palestinian cultural dresses. Here’s an overview of its features and components:

1. Overview
HennaStoreApp is an e-commerce platform that focuses on traditional Palestinian fashion. It allows users to browse, purchase, and learn about various Palestinian dresses and accessories.

2. Key Features
Product Listings: The app features a catalog of Palestinian dresses, complete with images, descriptions, and pricing information.
User Authentication: Users can register, log in, and manage their accounts.
Shopping Cart: Customers can add items to their cart, select sizes, and proceed to checkout.
Order Management: Users can view their order history and track their orders.
Admin Dashboard: Admins can manage products, users, and orders from a dedicated backend interface.
3. Technical Details
Framework: Django (version 3.2.25)
Database: PostgreSQL (as per recent changes from SQLite)
Front End: HTML, CSS, JavaScript
Styling: The app uses various CSS files and frameworks for styling.
4. Models
Dress: Represents the dresses available for sale, including fields like name, description, price, and images.
User: Handles user information and authentication.
Order: Manages user orders, including order status and total amount.
Category: Categorizes dresses into different types for easier browsing.
5. Admin Interface
The admin dashboard is built to manage:

Users: Add, edit, and delete user accounts.
Products: Manage product listings, including adding new dresses and updating existing ones.
Orders: Track and manage customer orders and their statuses.
6. Deployment
Web Server: Nginx (configured to serve the Django application)
Database Management: PostgreSQL, with adjustments made to the database configuration as needed.
Error Handling: The app handles various errors, including database connection issues and missing tables.
7. Recent Updates
Transitioned from SQLite to PostgreSQL for better performance and scalability.
Implemented features to manage product sizes and search functionality.
8. Challenges and Solutions
Database Migration: Migrating from SQLite to PostgreSQL required updating the database configuration and handling migration issues.
Nginx Configuration: Resolved conflicts related to port binding and ensured proper server configuration.
9. Future Plans
Feature Expansion: Plans to add men’s traditional clothes and expand the product range.
Enhanced User Experience: Improvements to the user interface and additional functionalities based on user feedback.
If you have any specific questions about HennaStoreApp or need help with particular features or issues, feel free to ask!
