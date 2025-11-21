/**
 * Tests for JSON to XML Translator
 */

import { test } from 'node:test';
import assert from 'node:assert';
import { jsonToXml, jsonStringToXml, escapeXml, isValidXmlName, sanitizeKey } from './index.js';

test('escapeXml should escape special XML characters', () => {
  assert.strictEqual(escapeXml('Hello & World'), 'Hello &amp; World');
  assert.strictEqual(escapeXml('<tag>'), '&lt;tag&gt;');
  assert.strictEqual(escapeXml('"quoted"'), '&quot;quoted&quot;');
  assert.strictEqual(escapeXml("'single'"), '&apos;single&apos;');
  assert.strictEqual(escapeXml('a<b>c&d"e\'f'), 'a&lt;b&gt;c&amp;d&quot;e&apos;f');
});

test('escapeXml should handle null and undefined', () => {
  assert.strictEqual(escapeXml(null), '');
  assert.strictEqual(escapeXml(undefined), '');
});

test('isValidXmlName should validate XML element names', () => {
  assert.strictEqual(isValidXmlName('validName'), true);
  assert.strictEqual(isValidXmlName('_validName'), true);
  assert.strictEqual(isValidXmlName('valid-name'), true);
  assert.strictEqual(isValidXmlName('valid.name'), true);
  assert.strictEqual(isValidXmlName('valid123'), true);
  assert.strictEqual(isValidXmlName('123invalid'), false);
  assert.strictEqual(isValidXmlName('invalid name'), false);
  assert.strictEqual(isValidXmlName('invalid@name'), false);
});

test('sanitizeKey should convert invalid keys to valid XML names', () => {
  assert.strictEqual(sanitizeKey('validName'), 'validName');
  assert.strictEqual(sanitizeKey('invalid name'), 'invalid_name');
  assert.strictEqual(sanitizeKey('123invalid'), '_123invalid');
  assert.strictEqual(sanitizeKey('invalid@name'), 'invalid_name');
  assert.strictEqual(sanitizeKey(''), 'item');
  assert.strictEqual(sanitizeKey(null), 'item');
});

test('jsonToXml should convert simple object', () => {
  const json = { name: 'John', age: 30 };
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<?xml version="1.0" encoding="UTF-8"?>'));
  assert.ok(xml.includes('<root>'));
  assert.ok(xml.includes('<name>John</name>'));
  assert.ok(xml.includes('<age>30</age>'));
  assert.ok(xml.includes('</root>'));
});

test('jsonToXml should convert nested object', () => {
  const json = {
    person: {
      name: 'John',
      address: {
        city: 'New York',
        zip: '10001'
      }
    }
  };
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<person>'));
  assert.ok(xml.includes('<name>John</name>'));
  assert.ok(xml.includes('<address>'));
  assert.ok(xml.includes('<city>New York</city>'));
  assert.ok(xml.includes('<zip>10001</zip>'));
  assert.ok(xml.includes('</address>'));
  assert.ok(xml.includes('</person>'));
});

test('jsonToXml should convert array', () => {
  const json = {
    items: [1, 2, 3]
  };
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<items>'));
  assert.ok(xml.includes('<item>1</item>'));
  assert.ok(xml.includes('<item>2</item>'));
  assert.ok(xml.includes('<item>3</item>'));
  assert.ok(xml.includes('</items>'));
});

test('jsonToXml should convert array of objects', () => {
  const json = {
    users: [
      { name: 'John', age: 30 },
      { name: 'Jane', age: 25 }
    ]
  };
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<users>'));
  assert.ok(xml.includes('<item>'));
  assert.ok(xml.includes('<name>John</name>'));
  assert.ok(xml.includes('<age>30</age>'));
  assert.ok(xml.includes('<name>Jane</name>'));
  assert.ok(xml.includes('<age>25</age>'));
  assert.ok(xml.includes('</users>'));
});

test('jsonToXml should handle null values', () => {
  const json = { value: null };
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<value />'));
});

test('jsonToXml should handle boolean values', () => {
  const json = { active: true, disabled: false };
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<active>true</active>'));
  assert.ok(xml.includes('<disabled>false</disabled>'));
});

test('jsonToXml should handle special characters in values', () => {
  const json = { message: 'Hello <World> & "Friends"' };
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<message>Hello &lt;World&gt; &amp; &quot;Friends&quot;</message>'));
});

test('jsonToXml should respect custom root element', () => {
  const json = { name: 'John' };
  const xml = jsonToXml(json, { rootElement: 'data' });
  
  assert.ok(xml.includes('<data>'));
  assert.ok(xml.includes('</data>'));
  assert.ok(!xml.includes('<root>'));
});

test('jsonToXml should respect custom array item name', () => {
  const json = { items: [1, 2, 3] };
  const xml = jsonToXml(json, { arrayItemName: 'element' });
  
  assert.ok(xml.includes('<element>1</element>'));
  assert.ok(xml.includes('<element>2</element>'));
  assert.ok(xml.includes('<element>3</element>'));
  assert.ok(!xml.includes('<item>'));
});

test('jsonToXml should respect custom indentation', () => {
  const json = { name: 'John' };
  const xml = jsonToXml(json, { indentSize: 4 });
  
  assert.ok(xml.includes('    <name>John</name>'));
});

test('jsonToXml should omit XML declaration when requested', () => {
  const json = { name: 'John' };
  const xml = jsonToXml(json, { includeDeclaration: false });
  
  assert.ok(!xml.includes('<?xml'));
  assert.ok(xml.includes('<root>'));
});

test('jsonToXml should handle empty object', () => {
  const json = {};
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<root>'));
  assert.ok(xml.includes('</root>'));
});

test('jsonToXml should handle empty array', () => {
  const json = [];
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<root>'));
  assert.ok(xml.includes('</root>'));
});

test('jsonToXml should handle primitive value at root', () => {
  const json = 'Hello World';
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<root>Hello World</root>'));
});

test('jsonToXml should handle number at root', () => {
  const json = 42;
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<root>42</root>'));
});

test('jsonToXml should handle complex nested structure', () => {
  const json = {
    company: {
      name: 'Tech Corp',
      employees: [
        {
          name: 'John',
          skills: ['JavaScript', 'Python'],
          active: true
        },
        {
          name: 'Jane',
          skills: ['Java', 'C++'],
          active: false
        }
      ],
      location: {
        city: 'San Francisco',
        country: 'USA'
      }
    }
  };
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<company>'));
  assert.ok(xml.includes('<name>Tech Corp</name>'));
  assert.ok(xml.includes('<employees>'));
  assert.ok(xml.includes('<name>John</name>'));
  assert.ok(xml.includes('<skills>'));
  assert.ok(xml.includes('<item>JavaScript</item>'));
  assert.ok(xml.includes('<item>Python</item>'));
  assert.ok(xml.includes('<active>true</active>'));
  assert.ok(xml.includes('<location>'));
  assert.ok(xml.includes('<city>San Francisco</city>'));
});

test('jsonStringToXml should parse and convert JSON string', () => {
  const jsonString = '{"name":"John","age":30}';
  const xml = jsonStringToXml(jsonString);
  
  assert.ok(xml.includes('<name>John</name>'));
  assert.ok(xml.includes('<age>30</age>'));
});

test('jsonStringToXml should throw error for invalid JSON', () => {
  const invalidJson = '{invalid json}';
  
  assert.throws(() => {
    jsonStringToXml(invalidJson);
  }, /Failed to parse JSON/);
});

test('jsonToXml should handle keys with invalid XML characters', () => {
  const json = {
    'invalid key': 'value1',
    '123numeric': 'value2',
    'special@char': 'value3'
  };
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<invalid_key>value1</invalid_key>'));
  assert.ok(xml.includes('<_123numeric>value2</_123numeric>'));
  assert.ok(xml.includes('<special_char>value3</special_char>'));
});

test('jsonToXml should handle mixed array types', () => {
  const json = {
    mixed: [1, 'string', true, null, { key: 'value' }]
  };
  const xml = jsonToXml(json);
  
  assert.ok(xml.includes('<item>1</item>'));
  assert.ok(xml.includes('<item>string</item>'));
  assert.ok(xml.includes('<item>true</item>'));
  assert.ok(xml.includes('<item />'));
  assert.ok(xml.includes('<key>value</key>'));
});

console.log('All tests completed!');
