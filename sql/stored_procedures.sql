-- Fictional demonstration procedures; MySQL 8.0.29+ / 8.4.
-- IF NOT EXISTS preserves any existing routine definitions.
-- Mutating procedures deliberately do not COMMIT: Python owns the transaction.
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS GetMaxQuantity()
BEGIN
    SELECT COALESCE(MAX(Quantity), 0) AS MaxQuantity FROM OrderItems;
END$$

CREATE PROCEDURE IF NOT EXISTS ManageBooking(
    IN p_BookingID INT UNSIGNED,
    IN p_BookingDate DATE,
    IN p_BookingSlot TIME,
    IN p_TableNo SMALLINT UNSIGNED,
    IN p_CustomerID INT UNSIGNED,
    IN p_EmployeeID INT UNSIGNED
)
BEGIN
    IF p_BookingID IS NULL OR p_BookingID = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A positive booking identifier is required';
    END IF;
    IF p_BookingDate IS NULL OR p_BookingDate < CURRENT_DATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking date must be today or later';
    END IF;
    IF p_BookingSlot IS NULL OR p_BookingSlot NOT BETWEEN '10:00:00' AND '20:00:00'
       OR MINUTE(p_BookingSlot) <> 0 OR SECOND(p_BookingSlot) <> 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Choose a whole-hour slot from 10 AM through 8 PM';
    END IF;
    IF p_BookingDate = CURRENT_DATE() AND p_BookingSlot <= CURRENT_TIME() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking time must be in the future';
    END IF;
    IF p_TableNo IS NULL OR p_TableNo NOT BETWEEN 1 AND 50 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Table number must be between 1 and 50';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerID = p_CustomerID) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Customer does not exist';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM Employees WHERE EmployeeID = p_EmployeeID) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Employee does not exist';
    END IF;
    IF EXISTS (SELECT 1 FROM Bookings WHERE BookingID = p_BookingID) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking identifier already exists; no record was overwritten';
    END IF;
    INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
    VALUES (p_BookingID, p_BookingDate, p_BookingSlot, p_TableNo, p_CustomerID, p_EmployeeID);
    SELECT p_BookingID AS BookingID, 'Booking created; commit required' AS Status;
END$$

CREATE PROCEDURE IF NOT EXISTS UpdateBooking(
    IN p_BookingID INT UNSIGNED,
    IN p_BookingDate DATE,
    IN p_BookingSlot TIME
)
BEGIN
    DECLARE v_BookingID INT UNSIGNED DEFAULT NULL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_BookingID = NULL;
    IF p_BookingDate IS NULL OR p_BookingDate < CURRENT_DATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking date must be today or later';
    END IF;
    IF p_BookingSlot IS NULL OR p_BookingSlot NOT BETWEEN '10:00:00' AND '20:00:00'
       OR MINUTE(p_BookingSlot) <> 0 OR SECOND(p_BookingSlot) <> 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Choose a whole-hour slot from 10 AM through 8 PM';
    END IF;
    IF p_BookingDate = CURRENT_DATE() AND p_BookingSlot <= CURRENT_TIME() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking time must be in the future';
    END IF;
    SELECT BookingID INTO v_BookingID FROM Bookings
    WHERE BookingID = p_BookingID FOR UPDATE;
    IF v_BookingID IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking does not exist';
    END IF;
    IF EXISTS (SELECT 1 FROM Orders WHERE BookingID = p_BookingID) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Bookings linked to sales history cannot be rescheduled';
    END IF;
    UPDATE Bookings SET BookingDate = p_BookingDate, BookingSlot = p_BookingSlot
    WHERE BookingID = p_BookingID;
    SELECT p_BookingID AS BookingID, 'Booking updated; commit required' AS Status;
END$$

CREATE PROCEDURE IF NOT EXISTS CancelBooking(IN p_BookingID INT UNSIGNED)
BEGIN
    DECLARE v_BookingID INT UNSIGNED DEFAULT NULL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_BookingID = NULL;
    SELECT BookingID INTO v_BookingID FROM Bookings
    WHERE BookingID = p_BookingID FOR UPDATE;
    IF v_BookingID IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking does not exist';
    END IF;
    IF EXISTS (SELECT 1 FROM Orders WHERE BookingID = p_BookingID) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Bookings linked to sales history cannot be deleted';
    END IF;
    DELETE FROM Bookings WHERE BookingID = p_BookingID;
    SELECT p_BookingID AS BookingID, 'Booking cancelled; commit required' AS Status;
END$$

CREATE PROCEDURE IF NOT EXISTS GetSalesReport()
BEGIN
    SELECT COUNT(*) AS TotalOrders,
           COALESCE(SUM(TotalCost), 0.00) AS TotalSales,
           COALESCE(ROUND(AVG(TotalCost), 2), 0.00) AS AverageOrderValue,
           COALESCE(MAX(TotalCost), 0.00) AS HighestOrderValue,
           COALESCE(MIN(TotalCost), 0.00) AS LowestOrderValue
    FROM Orders;
END$$

CREATE PROCEDURE IF NOT EXISTS GetCustomerOrders(IN p_CustomerID INT UNSIGNED)
BEGIN
    SELECT c.CustomerID, c.CustomerName, o.OrderID, o.OrderDate,
           o.BookingID, o.TableNo, o.TotalCost
    FROM Customers AS c
    JOIN Orders AS o ON o.CustomerID = c.CustomerID
    WHERE c.CustomerID = p_CustomerID
    ORDER BY o.OrderDate, o.OrderID;
END$$

CREATE PROCEDURE IF NOT EXISTS GetPopularMenuItems()
BEGIN
    SELECT m.ItemID, m.ItemName, m.Type,
           COALESCE(SUM(oi.Quantity), 0) AS QuantitySold,
           COALESCE(SUM(oi.Quantity * oi.UnitPrice), 0.00) AS ItemSales
    FROM MenuItems AS m
    LEFT JOIN OrderItems AS oi ON oi.ItemID = m.ItemID
    GROUP BY m.ItemID, m.ItemName, m.Type
    ORDER BY QuantitySold DESC, m.ItemID;
END$$

CREATE PROCEDURE IF NOT EXISTS GetEmployeeBookings()
BEGIN
    SELECT e.EmployeeID, e.Name AS EmployeeName, e.Role,
           b.BookingID, b.BookingDate, b.BookingSlot, b.TableNo,
           c.CustomerID, c.CustomerName
    FROM Employees AS e
    JOIN Bookings AS b ON b.EmployeeID = e.EmployeeID
    JOIN Customers AS c ON c.CustomerID = b.CustomerID
    ORDER BY e.EmployeeID, b.BookingDate, b.BookingSlot, b.BookingID;
END$$
DELIMITER ;
