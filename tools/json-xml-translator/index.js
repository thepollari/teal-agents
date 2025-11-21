/**
 * JSON to XML Translator
 * Converts JSON objects to XML format
 */

/**
 * Escapes special XML characters in text content
 * @param {string} text - The text to escape
 * @returns {string} - The escaped text
 */
export function escapeXml(text) {
  if (text === null || text === undefined) {
    return '';
  }
  
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * Validates if a string is a valid XML element name
 * @param {string} name - The name to validate
 * @returns {boolean} - True if valid, false otherwise
 */
export function isValidXmlName(name) {
  const xmlNameRegex = /^[a-zA-Z_][\w.-]*$/;
  return xmlNameRegex.test(name);
}

/**
 * Sanitizes a key to be a valid XML element name
 * @param {string} key - The key to sanitize
 * @returns {string} - A valid XML element name
 */
export function sanitizeKey(key) {
  if (!key || typeof key !== 'string') {
    return 'item';
  }
  
  let sanitized = key.replace(/[^\w.-]/g, '_');
  
  if (!/^[a-zA-Z_]/.test(sanitized)) {
    sanitized = '_' + sanitized;
  }
  
  return sanitized;
}

/**
 * Converts a JSON value to XML string
 * @param {*} value - The value to convert
 * @param {string} key - The key/tag name for this value
 * @param {number} indent - Current indentation level
 * @param {Object} options - Conversion options
 * @returns {string} - The XML representation
 */
function valueToXml(value, key, indent = 0, options = {}) {
  const {
    indentSize = 2,
    arrayItemName = 'item',
    includeDeclaration = false,
    rootElement = 'root'
  } = options;
  
  const spaces = ' '.repeat(indent * indentSize);
  const tagName = sanitizeKey(key);
  
  if (value === null || value === undefined) {
    return `${spaces}<${tagName} />\n`;
  }
  
  if (Array.isArray(value)) {
    let xml = `${spaces}<${tagName}>\n`;
    value.forEach((item, index) => {
      xml += valueToXml(item, arrayItemName, indent + 1, options);
    });
    xml += `${spaces}</${tagName}>\n`;
    return xml;
  }
  
  if (typeof value === 'object') {
    let xml = `${spaces}<${tagName}>\n`;
    for (const [childKey, childValue] of Object.entries(value)) {
      xml += valueToXml(childValue, childKey, indent + 1, options);
    }
    xml += `${spaces}</${tagName}>\n`;
    return xml;
  }
  
  const escapedValue = escapeXml(value);
  return `${spaces}<${tagName}>${escapedValue}</${tagName}>\n`;
}

/**
 * Converts a JSON object to XML string
 * @param {Object|Array|*} json - The JSON data to convert
 * @param {Object} options - Conversion options
 * @param {number} options.indentSize - Number of spaces for indentation (default: 2)
 * @param {string} options.arrayItemName - Tag name for array items (default: 'item')
 * @param {boolean} options.includeDeclaration - Include XML declaration (default: true)
 * @param {string} options.rootElement - Root element name (default: 'root')
 * @returns {string} - The XML string
 */
export function jsonToXml(json, options = {}) {
  const {
    indentSize = 2,
    arrayItemName = 'item',
    includeDeclaration = true,
    rootElement = 'root'
  } = options;
  
  let xml = '';
  
  if (includeDeclaration) {
    xml += '<?xml version="1.0" encoding="UTF-8"?>\n';
  }
  
  if (json === null || json === undefined) {
    xml += `<${rootElement} />\n`;
  } else if (Array.isArray(json)) {
    xml += `<${rootElement}>\n`;
    json.forEach((item) => {
      xml += valueToXml(item, arrayItemName, 1, { ...options, includeDeclaration: false });
    });
    xml += `</${rootElement}>\n`;
  } else if (typeof json === 'object') {
    xml += `<${rootElement}>\n`;
    for (const [key, value] of Object.entries(json)) {
      xml += valueToXml(value, key, 1, { ...options, includeDeclaration: false });
    }
    xml += `</${rootElement}>\n`;
  } else {
    const escapedValue = escapeXml(json);
    xml += `<${rootElement}>${escapedValue}</${rootElement}>\n`;
  }
  
  return xml;
}

/**
 * Converts a JSON string to XML string
 * @param {string} jsonString - The JSON string to convert
 * @param {Object} options - Conversion options
 * @returns {string} - The XML string
 * @throws {Error} - If JSON parsing fails
 */
export function jsonStringToXml(jsonString, options = {}) {
  try {
    const json = JSON.parse(jsonString);
    return jsonToXml(json, options);
  } catch (error) {
    throw new Error(`Failed to parse JSON: ${error.message}`);
  }
}

export default {
  jsonToXml,
  jsonStringToXml,
  escapeXml,
  isValidXmlName,
  sanitizeKey
};
