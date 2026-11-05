-- FICTIONAL DEMONSTRATION DATA: not the official course dataset.
-- The first five menu names/prices mirror the existing capstone seed, read without modifying it.
-- Other names, example.com contacts, dates, employees and sales are invented for this report.
-- Each deterministic ID is inserted only when absent; existing records are never overwritten.
-- Python commits the complete seed transaction only after all statements succeed.

-- Customers: 8 demonstration records.
INSERT INTO Customers (CustomerID, CustomerName, ContactNumber, Email)
SELECT 1001, 'Maya Bennett', '+1-202-555-0101', 'maya.bennett@example.com'
WHERE NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerID = 1001);
INSERT INTO Customers (CustomerID, CustomerName, ContactNumber, Email)
SELECT 1002, 'Omar Faris', '+1-202-555-0102', 'omar.faris@example.com'
WHERE NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerID = 1002);
INSERT INTO Customers (CustomerID, CustomerName, ContactNumber, Email)
SELECT 1003, 'Sofia Chen', '+1-202-555-0103', 'sofia.chen@example.com'
WHERE NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerID = 1003);
INSERT INTO Customers (CustomerID, CustomerName, ContactNumber, Email)
SELECT 1004, 'Daniel Ortiz', '+1-202-555-0104', 'daniel.ortiz@example.com'
WHERE NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerID = 1004);
INSERT INTO Customers (CustomerID, CustomerName, ContactNumber, Email)
SELECT 1005, 'Amira Patel', '+1-202-555-0105', 'amira.patel@example.com'
WHERE NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerID = 1005);
INSERT INTO Customers (CustomerID, CustomerName, ContactNumber, Email)
SELECT 1006, 'Lucas Reed', '+1-202-555-0106', 'lucas.reed@example.com'
WHERE NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerID = 1006);
INSERT INTO Customers (CustomerID, CustomerName, ContactNumber, Email)
SELECT 1007, 'Nora Hassan', '+1-202-555-0107', 'nora.hassan@example.com'
WHERE NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerID = 1007);
INSERT INTO Customers (CustomerID, CustomerName, ContactNumber, Email)
SELECT 1008, 'Ethan Brooks', '+1-202-555-0108', 'ethan.brooks@example.com'
WHERE NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerID = 1008);

-- Employees: 4 demonstration records.
INSERT INTO Employees (EmployeeID, Name, Role, Address, ContactNumber, Email, AnnualSalary)
SELECT 2001, 'Leila Morgan', 'Restaurant manager', '101 Demo Avenue, Example City', '+1-202-555-0121', 'leila.morgan@example.com', 62000.00
WHERE NOT EXISTS (SELECT 1 FROM Employees WHERE EmployeeID = 2001);
INSERT INTO Employees (EmployeeID, Name, Role, Address, ContactNumber, Email, AnnualSalary)
SELECT 2002, 'Samir Cole', 'Head chef', '102 Demo Avenue, Example City', '+1-202-555-0122', 'samir.cole@example.com', 58000.00
WHERE NOT EXISTS (SELECT 1 FROM Employees WHERE EmployeeID = 2002);
INSERT INTO Employees (EmployeeID, Name, Role, Address, ContactNumber, Email, AnnualSalary)
SELECT 2003, 'Elena Park', 'Server', '103 Demo Avenue, Example City', '+1-202-555-0123', 'elena.park@example.com', 36000.00
WHERE NOT EXISTS (SELECT 1 FROM Employees WHERE EmployeeID = 2003);
INSERT INTO Employees (EmployeeID, Name, Role, Address, ContactNumber, Email, AnnualSalary)
SELECT 2004, 'Theo James', 'Host', '104 Demo Avenue, Example City', '+1-202-555-0124', 'theo.james@example.com', 34000.00
WHERE NOT EXISTS (SELECT 1 FROM Employees WHERE EmployeeID = 2004);

-- MenuItems: 10 demonstration records.
INSERT INTO MenuItems (ItemID, ItemName, Type, Price)
SELECT 3001, 'Greek salad', 'Starters', 12.50
WHERE NOT EXISTS (SELECT 1 FROM MenuItems WHERE ItemID = 3001);
INSERT INTO MenuItems (ItemID, ItemName, Type, Price)
SELECT 3002, 'Bruschetta', 'Starters', 8.00
WHERE NOT EXISTS (SELECT 1 FROM MenuItems WHERE ItemID = 3002);
INSERT INTO MenuItems (ItemID, ItemName, Type, Price)
SELECT 3003, 'Lemon chicken', 'Mains', 19.50
WHERE NOT EXISTS (SELECT 1 FROM MenuItems WHERE ItemID = 3003);
INSERT INTO MenuItems (ItemID, ItemName, Type, Price)
SELECT 3004, 'Garden pasta', 'Mains', 16.00
WHERE NOT EXISTS (SELECT 1 FROM MenuItems WHERE ItemID = 3004);
INSERT INTO MenuItems (ItemID, ItemName, Type, Price)
SELECT 3005, 'Lemon dessert', 'Desserts', 7.50
WHERE NOT EXISTS (SELECT 1 FROM MenuItems WHERE ItemID = 3005);
INSERT INTO MenuItems (ItemID, ItemName, Type, Price)
SELECT 3006, 'Sparkling water', 'Beverages', 3.00
WHERE NOT EXISTS (SELECT 1 FROM MenuItems WHERE ItemID = 3006);
INSERT INTO MenuItems (ItemID, ItemName, Type, Price)
SELECT 3007, 'Lemonade', 'Beverages', 4.50
WHERE NOT EXISTS (SELECT 1 FROM MenuItems WHERE ItemID = 3007);
INSERT INTO MenuItems (ItemID, ItemName, Type, Price)
SELECT 3008, 'Espresso', 'Beverages', 3.50
WHERE NOT EXISTS (SELECT 1 FROM MenuItems WHERE ItemID = 3008);
INSERT INTO MenuItems (ItemID, ItemName, Type, Price)
SELECT 3009, 'Grilled sea bass', 'Mains', 24.00
WHERE NOT EXISTS (SELECT 1 FROM MenuItems WHERE ItemID = 3009);
INSERT INTO MenuItems (ItemID, ItemName, Type, Price)
SELECT 3010, 'Marinated olives', 'Starters', 5.00
WHERE NOT EXISTS (SELECT 1 FROM MenuItems WHERE ItemID = 3010);

-- Bookings: 12 demonstration records.
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4001, '2026-01-15', '12:00:00', 1, 1001, 2004
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4001);
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4002, '2026-01-15', '18:00:00', 2, 1002, 2003
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4002);
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4003, '2026-02-15', '12:00:00', 1, 1003, 2001
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4003);
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4004, '2026-02-15', '18:00:00', 2, 1004, 2004
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4004);
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4005, '2026-03-15', '12:00:00', 1, 1001, 2003
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4005);
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4006, '2026-03-15', '18:00:00', 2, 1005, 2001
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4006);
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4007, '2026-04-15', '12:00:00', 1, 1006, 2004
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4007);
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4008, '2026-04-15', '18:00:00', 2, 1002, 2003
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4008);
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4009, '2026-05-15', '12:00:00', 1, 1007, 2001
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4009);
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4010, '2026-05-15', '18:00:00', 2, 1008, 2004
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4010);
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4011, '2026-06-15', '12:00:00', 1, 1003, 2003
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4011);
INSERT INTO Bookings (BookingID, BookingDate, BookingSlot, TableNo, CustomerID, EmployeeID)
SELECT 4012, '2026-06-15', '18:00:00', 2, 1001, 2001
WHERE NOT EXISTS (SELECT 1 FROM Bookings WHERE BookingID = 4012);

-- Orders: 12 demonstration records.
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5001, 1001, 4001, '2026-01-15', 1, 73.00
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5001);
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5002, 1002, 4002, '2026-01-15', 2, 31.00
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5002);
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5003, 1003, 4003, '2026-02-15', 1, 39.50
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5003);
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5004, 1004, 4004, '2026-02-15', 2, 94.50
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5004);
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5005, 1001, 4005, '2026-03-15', 1, 60.00
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5005);
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5006, 1005, 4006, '2026-03-15', 2, 70.00
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5006);
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5007, 1006, 4007, '2026-04-15', 1, 75.00
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5007);
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5008, 1002, 4008, '2026-04-15', 2, 112.00
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5008);
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5009, 1007, 4009, '2026-05-15', 1, 35.00
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5009);
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5010, 1008, 4010, '2026-05-15', 2, 68.50
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5010);
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5011, 1003, 4011, '2026-06-15', 1, 64.00
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5011);
INSERT INTO Orders (OrderID, CustomerID, BookingID, OrderDate, TableNo, TotalCost)
SELECT 5012, 1001, 4012, '2026-06-15', 2, 112.50
WHERE NOT EXISTS (SELECT 1 FROM Orders WHERE OrderID = 5012);

-- OrderItems: 36 demonstration records.
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6001, 5001, 3001, 2, 12.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6001);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6002, 5001, 3003, 2, 19.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6002);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6003, 5001, 3007, 2, 4.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6003);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6004, 5002, 3002, 1, 8.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6004);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6005, 5002, 3004, 1, 16.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6005);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6006, 5002, 3008, 2, 3.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6006);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6007, 5003, 3001, 1, 12.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6007);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6008, 5003, 3009, 1, 24.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6008);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6009, 5003, 3006, 1, 3.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6009);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6010, 5004, 3003, 3, 19.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6010);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6011, 5004, 3005, 3, 7.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6011);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6012, 5004, 3007, 3, 4.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6012);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6013, 5005, 3002, 2, 8.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6013);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6014, 5005, 3004, 2, 16.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6014);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6015, 5005, 3006, 4, 3.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6015);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6016, 5006, 3009, 2, 24.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6016);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6017, 5006, 3005, 2, 7.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6017);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6018, 5006, 3008, 2, 3.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6018);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6019, 5007, 3001, 2, 12.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6019);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6020, 5007, 3004, 2, 16.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6020);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6021, 5007, 3007, 4, 4.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6021);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6022, 5008, 3003, 4, 19.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6022);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6023, 5008, 3002, 2, 8.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6023);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6024, 5008, 3006, 6, 3.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6024);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6025, 5009, 3009, 1, 24.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6025);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6026, 5009, 3005, 1, 7.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6026);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6027, 5009, 3008, 1, 3.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6027);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6028, 5010, 3003, 2, 19.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6028);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6029, 5010, 3004, 1, 16.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6029);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6030, 5010, 3007, 3, 4.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6030);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6031, 5011, 3001, 3, 12.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6031);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6032, 5011, 3002, 2, 8.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6032);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6033, 5011, 3008, 3, 3.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6033);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6034, 5012, 3009, 3, 24.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6034);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6035, 5012, 3005, 3, 7.50
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6035);
INSERT INTO OrderItems (OrderItemID, OrderID, ItemID, Quantity, UnitPrice)
SELECT 6036, 5012, 3006, 6, 3.00
WHERE NOT EXISTS (SELECT 1 FROM OrderItems WHERE OrderItemID = 6036);

-- OrderDeliveryStatus: 12 demonstration records.
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7001, 5001, '2026-01-15', 'Delivered'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7001);
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7002, 5002, '2026-01-15', 'Served'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7002);
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7003, 5003, '2026-02-15', 'Served'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7003);
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7004, 5004, '2026-02-15', 'Delivered'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7004);
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7005, 5005, '2026-03-15', 'Served'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7005);
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7006, 5006, '2026-03-15', 'Served'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7006);
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7007, 5007, '2026-04-15', 'Delivered'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7007);
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7008, 5008, '2026-04-15', 'Served'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7008);
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7009, 5009, '2026-05-15', 'Served'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7009);
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7010, 5010, '2026-05-15', 'Delivered'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7010);
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7011, 5011, '2026-06-15', 'Served'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7011);
INSERT INTO OrderDeliveryStatus (DeliveryID, OrderID, DeliveryDate, DeliveryStatus)
SELECT 7012, 5012, '2026-06-15', 'Served'
WHERE NOT EXISTS (SELECT 1 FROM OrderDeliveryStatus WHERE DeliveryID = 7012);
