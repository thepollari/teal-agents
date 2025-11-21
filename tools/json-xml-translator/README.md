# JSON to XML Translator

A Node.js interface for translating JSON data to XML format. This tool provides both a programmatic API and a command-line interface for converting JSON objects to well-formed XML documents.

## Features

- Convert JSON objects, arrays, and primitive values to XML
- Proper handling of nested structures
- XML character escaping for special characters
- Customizable root element name
- Customizable array item element names
- Configurable indentation
- Optional XML declaration
- Command-line interface for easy usage
- Comprehensive test suite

## Requirements

- Node.js >= 18.0.0

## Installation

No external dependencies required. This tool uses only Node.js built-in modules.

```bash
cd tools/json-xml-translator
```

## Usage

### Command Line Interface

#### Basic Usage

Convert a JSON file to XML:

```bash
node cli.js input.json
```

Convert from stdin:

```bash
echo '{"name":"John","age":30}' | node cli.js
```

#### Options

- `-h, --help` - Show help message
- `-o, --output <file>` - Write output to file instead of stdout
- `-i, --indent <size>` - Indentation size (default: 2)
- `-r, --root <name>` - Root element name (default: 'root')
- `-a, --array-item <name>` - Array item element name (default: 'item')
- `--no-declaration` - Omit XML declaration

#### Examples

Convert and save to file:

```bash
node cli.js input.json -o output.xml
```

Custom root element:

```bash
node cli.js input.json -r data
```

Custom indentation:

```bash
node cli.js input.json -i 4
```

Custom array item names:

```bash
node cli.js input.json -a element
```

Omit XML declaration:

```bash
node cli.js input.json --no-declaration
```

### Programmatic API

#### Import the Module

```javascript
import { jsonToXml, jsonStringToXml } from './index.js';
```

#### Convert JSON Object to XML

```javascript
const json = {
  person: {
    name: 'John Doe',
    age: 30,
    email: 'john@example.com'
  }
};

const xml = jsonToXml(json);
console.log(xml);
```

Output:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
  <person>
    <name>John Doe</name>
    <age>30</age>
    <email>john@example.com</email>
  </person>
</root>
```

#### Convert JSON String to XML

```javascript
const jsonString = '{"name":"John","age":30}';
const xml = jsonStringToXml(jsonString);
console.log(xml);
```

#### Custom Options

```javascript
const json = {
  users: [
    { name: 'John', age: 30 },
    { name: 'Jane', age: 25 }
  ]
};

const xml = jsonToXml(json, {
  rootElement: 'data',
  arrayItemName: 'user',
  indentSize: 4,
  includeDeclaration: false
});

console.log(xml);
```

Output:

```xml
<data>
    <users>
        <user>
            <name>John</name>
            <age>30</age>
        </user>
        <user>
            <name>Jane</name>
            <age>25</age>
        </user>
    </users>
</data>
```

## API Reference

### `jsonToXml(json, options)`

Converts a JSON object to XML string.

**Parameters:**

- `json` (Object|Array|*) - The JSON data to convert
- `options` (Object) - Optional conversion options
  - `indentSize` (number) - Number of spaces for indentation (default: 2)
  - `arrayItemName` (string) - Tag name for array items (default: 'item')
  - `includeDeclaration` (boolean) - Include XML declaration (default: true)
  - `rootElement` (string) - Root element name (default: 'root')

**Returns:** (string) - The XML string

### `jsonStringToXml(jsonString, options)`

Converts a JSON string to XML string.

**Parameters:**

- `jsonString` (string) - The JSON string to convert
- `options` (Object) - Optional conversion options (same as `jsonToXml`)

**Returns:** (string) - The XML string

**Throws:** Error if JSON parsing fails

### `escapeXml(text)`

Escapes special XML characters in text content.

**Parameters:**

- `text` (string) - The text to escape

**Returns:** (string) - The escaped text

### `isValidXmlName(name)`

Validates if a string is a valid XML element name.

**Parameters:**

- `name` (string) - The name to validate

**Returns:** (boolean) - True if valid, false otherwise

### `sanitizeKey(key)`

Sanitizes a key to be a valid XML element name.

**Parameters:**

- `key` (string) - The key to sanitize

**Returns:** (string) - A valid XML element name

## Data Type Handling

### Objects

JSON objects are converted to XML elements with nested child elements:

```javascript
{ name: 'John', age: 30 }
```

```xml
<root>
  <name>John</name>
  <age>30</age>
</root>
```

### Arrays

Arrays are converted to a parent element with child elements for each item:

```javascript
{ items: [1, 2, 3] }
```

```xml
<root>
  <items>
    <item>1</item>
    <item>2</item>
    <item>3</item>
  </items>
</root>
```

### Null Values

Null values are converted to self-closing tags:

```javascript
{ value: null }
```

```xml
<root>
  <value />
</root>
```

### Boolean Values

Boolean values are converted to their string representation:

```javascript
{ active: true, disabled: false }
```

```xml
<root>
  <active>true</active>
  <disabled>false</disabled>
</root>
```

### Special Characters

Special XML characters are automatically escaped:

```javascript
{ message: 'Hello <World> & "Friends"' }
```

```xml
<root>
  <message>Hello &lt;World&gt; &amp; &quot;Friends&quot;</message>
</root>
```

### Invalid XML Element Names

Keys with invalid XML characters are automatically sanitized:

```javascript
{ 'invalid key': 'value', '123numeric': 'value' }
```

```xml
<root>
  <invalid_key>value</invalid_key>
  <_123numeric>value</_123numeric>
</root>
```

## Testing

Run the test suite:

```bash
npm test
```

The test suite includes 24 comprehensive tests covering:
- XML character escaping
- XML name validation and sanitization
- Simple and nested object conversion
- Array handling
- Null and boolean values
- Special characters
- Custom options
- Edge cases

## License

MIT
