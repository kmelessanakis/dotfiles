---
name: salesforce-apex-doc
description: Generate proper ApexDoc documentation comments for Salesforce Apex classes, methods, properties, and interfaces. Use this skill for documenting Apex code, adding code comments, creating method documentation, class documentation, or when asked to add ApexDoc, Javadoc-style comments, or documentation to Apex files.
---

# ApexDoc Generation Skill

## Overview
This skill provides guidelines for creating proper ApexDoc documentation comments in Salesforce Apex code. ApexDoc uses a Javadoc-style syntax to document classes, methods, properties, and other code elements.

## When to Use This Skill
- When asked to document Apex classes, methods, or properties
- When creating new Apex code that needs documentation
- When improving existing Apex code with proper documentation
- When asked to add comments, ApexDoc, or documentation to Apex files
- During code reviews when documentation is missing or incomplete

## ApexDoc Syntax

### Basic Structure
ApexDoc comments start with `/**` and end with `*/`. Each line within the comment typically starts with `*`.

```apex
/**
 * Brief description of what this class/method does.
 * 
 * Detailed description with more context if needed.
 * Can span multiple lines.
 * 
 * @param parameterName Description of the parameter
 * @return Description of the return value
 * @throws ExceptionType Description of when this exception is thrown
 */
```

### Common ApexDoc Tags

#### @description
Provides a detailed description of the code element. Can be omitted if description is provided directly after the opening comment.

```apex
/**
 * @description Calculates the total price including tax
 */
```

#### @param
Documents method parameters. Include one @param tag for each parameter.

```apex
/**
 * @param accountId The ID of the account to retrieve
 * @param includeContacts Whether to include related contacts
 */
public static Account getAccount(Id accountId, Boolean includeContacts) { }
```

#### @return
Documents the return value of a method.

```apex
/**
 * @return The calculated total price as a Decimal
 */
public Decimal calculateTotal() { }
```

#### @throws or @exception
Documents exceptions that may be thrown by the method.

```apex
/**
 * @throws DmlException If the database operation fails
 * @throws InvalidParameterException If accountId is null
 */
```

#### @example
Provides usage examples for the method or class.

```apex
/**
 * @example
 * Account acc = AccountService.getAccount('001xx000003DIlo');
 * System.debug('Account Name: ' + acc.Name);
 */
```

#### @see
References related classes or methods.

```apex
/**
 * @see ContactService
 * @see AccountTriggerHandler
 */
```

#### @deprecated
Marks code as deprecated and should include guidance on what to use instead.

```apex
/**
 * @deprecated Use getAccountWithContacts() instead
 */
```

## Documentation Examples

### Class Documentation

```apex
/**
 * Service class for managing Account records and related operations.
 * 
 * This class provides methods for querying, creating, updating, and deleting
 * Account records with proper error handling and field-level security checks.
 * 
 * @see ContactService
 */
public with sharing class AccountService {
    // Class implementation
}
```

### Method Documentation

```apex
/**
 * Retrieves an Account record by its ID with optional related contacts.
 * 
 * This method performs a SOQL query to fetch the Account record and optionally
 * includes related Contact records based on the includeContacts parameter.
 * 
 * @param accountId The unique identifier of the Account to retrieve
 * @param includeContacts If true, includes related Contact records in the query
 * @return The Account record with requested data, or null if not found
 * @throws QueryException If the SOQL query fails
 * @throws SecurityException If user lacks read access to Account object
 * 
 * @example
 * Account acc = AccountService.getAccount('001xx000003DIlo', true);
 * System.debug('Account has ' + acc.Contacts.size() + ' contacts');
 */
public static Account getAccount(Id accountId, Boolean includeContacts) {
    // Method implementation
}
```

### Property Documentation

```apex
/**
 * The maximum number of records to process in a single transaction.
 * Default value is 200 to stay within governor limits.
 */
public static final Integer MAX_BATCH_SIZE = 200;

/**
 * Stores the current user's account for caching purposes.
 * This property is populated on first access and reused throughout the transaction.
 */
private Account currentUserAccount { get; set; }
```

### Constructor Documentation

```apex
/**
 * Creates a new instance of AccountService with default settings.
 * 
 * Initializes internal caches and sets up default query parameters.
 */
public AccountService() {
    // Constructor implementation
}

/**
 * Creates a new instance of AccountService with custom batch size.
 * 
 * @param batchSize The maximum number of records to process per batch
 * @throws IllegalArgumentException If batchSize is less than 1 or greater than 200
 */
public AccountService(Integer batchSize) {
    // Constructor implementation
}
```

### Interface Documentation

```apex
/**
 * Interface for services that process order records.
 * 
 * Implementations of this interface should handle order validation,
 * processing, and status updates according to business rules.
 * 
 */
public interface IOrderProcessor {
    /**
     * Processes a single order record.
     * 
     * @param order The Order record to process
     * @return True if processing was successful, false otherwise
     */
    Boolean processOrder(Order order);
}
```

### Enum Documentation

```apex
/**
 * Defines the possible states of an order throughout its lifecycle.
 */
public enum OrderStatus {
    /** Order has been created but not yet submitted */
    DRAFT,
    /** Order has been submitted and is awaiting approval */
    PENDING,
    /** Order has been approved and is being processed */
    APPROVED,
    /** Order has been completed successfully */
    COMPLETED,
    /** Order has been cancelled by user or system */
    CANCELLED
}
```

## Best Practices

### 1. Document All Public Methods and Classes
Every public or global class, method, and property should have ApexDoc comments.

### 2. Be Clear and Concise
- Start with a brief summary in the first sentence
- Add detailed explanations in subsequent paragraphs if needed
- Use clear, professional language

### 3. Document Parameters Thoroughly
- Explain what each parameter represents
- Specify any constraints (e.g., "must not be null", "must be positive")
- Indicate optional vs. required parameters

### 4. Explain Return Values
- Describe what the method returns
- Specify possible return values (e.g., "returns null if not found")
- Indicate the type and meaning of the return value

### 5. Document Exceptions
- List all exceptions that callers need to handle
- Explain under what conditions each exception is thrown

### 6. Provide Examples When Helpful
- Include code examples for complex methods
- Show typical usage patterns
- Demonstrate edge cases if relevant

### 7. Keep Documentation Up to Date
- Update comments when changing method signatures
- Mark deprecated code appropriately with migration guidance
- Review documentation during code reviews

### 8. Use Proper Grammar and Formatting
- Start descriptions with capital letters
- End with periods
- Use proper punctuation
- Maintain consistent style across the codebase

### 9. Document Business Logic
- Explain the "why" behind complex logic
- Reference business rules or requirements when applicable
- Note any important assumptions or constraints

### 10. Avoid Redundant Information
- Don't just restate the method name in the description
- Add value beyond what the code itself conveys
- Focus on intent, behavior, and usage

## Common Patterns

### CRUD Operations

```apex
/**
 * Creates a new Account record with the specified name and type.
 * 
 * This method performs field-level security checks before insertion
 * and returns the created Account with its newly assigned ID.
 * 
 * @param accountName The name for the new Account
 * @param accountType The type of Account (e.g., 'Customer', 'Partner')
 * @return The newly created Account record with ID
 * @throws DmlException If the insert operation fails
 * @throws SecurityException If user lacks create access to Account
 */
public static Account createAccount(String accountName, String accountType) {
    // Implementation
}
```

### Query Methods

```apex
/**
 * Queries and returns all Accounts matching the specified criteria.
 * 
 * Results are limited to the specified maximum number of records
 * and are ordered by Name ascending.
 * 
 * @param accountType The type of Accounts to query
 * @param maxRecords The maximum number of records to return (max: 2000)
 * @return List of Account records matching criteria, empty list if none found
 * @throws QueryException If the SOQL query fails
 */
public static List<Account> getAccountsByType(String accountType, Integer maxRecords) {
    // Implementation
}
```

### Validation Methods

```apex
/**
 * Validates whether the provided Account meets all business rules.
 * 
 * Checks include:
 * - Required fields are populated
 * - Email format is valid
 * - Phone number follows the correct pattern
 * - Account type is allowed
 * 
 * @param account The Account record to validate
 * @return True if all validations pass, false otherwise
 */
public static Boolean validateAccount(Account account) {
    // Implementation
}
```

### Utility Methods

```apex
/**
 * Converts a list of Account records to a map keyed by Account ID.
 * 
 * This utility method simplifies lookups when processing related records.
 * Null or empty input lists return an empty map.
 * 
 * @param accounts List of Account records to convert
 * @return Map with Account IDs as keys and Account records as values
 */
public static Map<Id, Account> accountsToMap(List<Account> accounts) {
    // Implementation
}
```

## Template for Quick Start

```apex
/**
 * [Brief one-line description of what this class/method does]
 * 
 * [Optional: More detailed description providing context, explaining
 * business logic, or describing the overall approach]
 * 
 * @param [paramName] [Description of parameter]
 * @return [Description of return value]
 * @throws [ExceptionType] [When this exception occurs]
 * 
 * @example
 * [Code example showing typical usage]
 * 
 * @see [RelatedClass]
 */
```

## Summary
When documenting Apex code, always:
1. Use the `/** */` comment style for ApexDoc
2. Include descriptions for all public/global elements
3. Document all parameters with @param
4. Document return values with @return
5. Document exceptions with @throws
6. Add examples for complex methods with @example
7. Keep documentation synchronized with code changes
8. Write clear, professional, and helpful documentation