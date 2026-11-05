-- Fictional demonstration schema for little_lemon_sales only.
-- Select the dedicated database through the pooled connection before execution.
-- MySQL DDL implicitly commits; these IF NOT EXISTS statements never replace tables.
CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INT UNSIGNED NOT NULL PRIMARY KEY,
    CustomerName VARCHAR(100) NOT NULL,
    ContactNumber VARCHAR(30) NOT NULL,
    Email VARCHAR(150) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Employees (
    EmployeeID INT UNSIGNED NOT NULL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Role VARCHAR(60) NOT NULL,
    Address VARCHAR(255) NOT NULL,
    ContactNumber VARCHAR(30) NOT NULL,
    Email VARCHAR(150) NOT NULL UNIQUE,
    AnnualSalary DECIMAL(10,2) NOT NULL,
    CONSTRAINT chk_employee_salary CHECK (AnnualSalary >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS MenuItems (
    ItemID INT UNSIGNED NOT NULL PRIMARY KEY,
    ItemName VARCHAR(100) NOT NULL,
    Type VARCHAR(40) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    CONSTRAINT chk_menu_price CHECK (Price > 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Bookings (
    BookingID INT UNSIGNED NOT NULL PRIMARY KEY,
    BookingDate DATE NOT NULL,
    BookingSlot TIME NOT NULL,
    TableNo SMALLINT UNSIGNED NOT NULL,
    CustomerID INT UNSIGNED NOT NULL,
    EmployeeID INT UNSIGNED NOT NULL,
    CONSTRAINT fk_booking_customer FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    CONSTRAINT fk_booking_employee FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
    CONSTRAINT uq_booking_table_slot UNIQUE (BookingDate, BookingSlot, TableNo),
    CONSTRAINT uq_booking_customer_table UNIQUE (BookingID, CustomerID, TableNo),
    CONSTRAINT chk_booking_table CHECK (TableNo BETWEEN 1 AND 50),
    CONSTRAINT chk_booking_slot CHECK (
        BookingSlot BETWEEN '10:00:00' AND '20:00:00'
        AND MINUTE(BookingSlot) = 0 AND SECOND(BookingSlot) = 0
    )
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Orders (
    OrderID INT UNSIGNED NOT NULL PRIMARY KEY,
    CustomerID INT UNSIGNED NOT NULL,
    BookingID INT UNSIGNED NOT NULL,
    OrderDate DATE NOT NULL,
    TableNo SMALLINT UNSIGNED NOT NULL,
    TotalCost DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_order_customer FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    CONSTRAINT fk_order_booking FOREIGN KEY (BookingID, CustomerID, TableNo)
        REFERENCES Bookings(BookingID, CustomerID, TableNo),
    CONSTRAINT chk_order_table CHECK (TableNo BETWEEN 1 AND 50),
    CONSTRAINT chk_order_total CHECK (TotalCost >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS OrderItems (
    OrderItemID INT UNSIGNED NOT NULL PRIMARY KEY,
    OrderID INT UNSIGNED NOT NULL,
    ItemID INT UNSIGNED NOT NULL,
    Quantity SMALLINT UNSIGNED NOT NULL,
    UnitPrice DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_orderitem_order FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    CONSTRAINT fk_orderitem_menu FOREIGN KEY (ItemID) REFERENCES MenuItems(ItemID),
    CONSTRAINT uq_orderitem UNIQUE (OrderID, ItemID),
    CONSTRAINT chk_orderitem_quantity CHECK (Quantity > 0),
    CONSTRAINT chk_orderitem_price CHECK (UnitPrice > 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS OrderDeliveryStatus (
    DeliveryID INT UNSIGNED NOT NULL PRIMARY KEY,
    OrderID INT UNSIGNED NOT NULL UNIQUE,
    DeliveryDate DATE NOT NULL,
    DeliveryStatus VARCHAR(20) NOT NULL,
    CONSTRAINT fk_delivery_order FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    CONSTRAINT chk_delivery_status CHECK (
        DeliveryStatus IN ('Pending', 'Preparing', 'Served', 'Delivered', 'Cancelled')
    )
) ENGINE=InnoDB;
