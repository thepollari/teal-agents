#!/usr/bin/env node

/**
 * CLI interface for JSON to XML Translator
 */

import { readFile, writeFile } from 'fs/promises';
import { stdin } from 'process';
import { jsonToXml, jsonStringToXml } from './index.js';

/**
 * Reads data from stdin
 * @returns {Promise<string>} - The data from stdin
 */
function readStdin() {
  return new Promise((resolve, reject) => {
    let data = '';
    
    stdin.setEncoding('utf8');
    
    stdin.on('data', (chunk) => {
      data += chunk;
    });
    
    stdin.on('end', () => {
      resolve(data);
    });
    
    stdin.on('error', (error) => {
      reject(error);
    });
  });
}

/**
 * Displays usage information
 */
function showHelp() {
  console.log(`
JSON to XML Translator

Usage:
  node cli.js [options] [input-file]

Options:
  -h, --help              Show this help message
  -o, --output <file>     Write output to file instead of stdout
  -i, --indent <size>     Indentation size (default: 2)
  -r, --root <name>       Root element name (default: 'root')
  -a, --array-item <name> Array item element name (default: 'item')
  --no-declaration        Omit XML declaration

Examples:
  # Convert from file
  node cli.js input.json

  # Convert from stdin
  echo '{"name":"John"}' | node cli.js

  # Convert and save to file
  node cli.js input.json -o output.xml

  # Custom root element
  node cli.js input.json -r data

  # Custom indentation
  node cli.js input.json -i 4
`);
}

/**
 * Parses command line arguments
 * @param {string[]} args - Command line arguments
 * @returns {Object} - Parsed options and input file
 */
function parseArgs(args) {
  const options = {
    indentSize: 2,
    rootElement: 'root',
    arrayItemName: 'item',
    includeDeclaration: true,
    outputFile: null,
    inputFile: null
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    switch (arg) {
      case '-h':
      case '--help':
        showHelp();
        process.exit(0);
        break;
        
      case '-o':
      case '--output':
        options.outputFile = args[++i];
        break;
        
      case '-i':
      case '--indent':
        options.indentSize = parseInt(args[++i], 10);
        if (isNaN(options.indentSize) || options.indentSize < 0) {
          console.error('Error: Indent size must be a non-negative number');
          process.exit(1);
        }
        break;
        
      case '-r':
      case '--root':
        options.rootElement = args[++i];
        break;
        
      case '-a':
      case '--array-item':
        options.arrayItemName = args[++i];
        break;
        
      case '--no-declaration':
        options.includeDeclaration = false;
        break;
        
      default:
        if (arg.startsWith('-')) {
          console.error(`Error: Unknown option '${arg}'`);
          console.error('Use --help for usage information');
          process.exit(1);
        } else {
          options.inputFile = arg;
        }
    }
  }
  
  return options;
}

/**
 * Main CLI function
 */
async function main() {
  try {
    const args = process.argv.slice(2);
    const options = parseArgs(args);
    
    let jsonString;
    
    if (options.inputFile) {
      try {
        jsonString = await readFile(options.inputFile, 'utf8');
      } catch (error) {
        console.error(`Error reading file '${options.inputFile}': ${error.message}`);
        process.exit(1);
      }
    } else {
      if (process.stdin.isTTY) {
        console.error('Error: No input provided');
        console.error('Provide a JSON file as argument or pipe JSON data to stdin');
        console.error('Use --help for usage information');
        process.exit(1);
      }
      
      try {
        jsonString = await readStdin();
      } catch (error) {
        console.error(`Error reading from stdin: ${error.message}`);
        process.exit(1);
      }
    }
    
    let xml;
    try {
      xml = jsonStringToXml(jsonString, {
        indentSize: options.indentSize,
        rootElement: options.rootElement,
        arrayItemName: options.arrayItemName,
        includeDeclaration: options.includeDeclaration
      });
    } catch (error) {
      console.error(`Error converting JSON to XML: ${error.message}`);
      process.exit(1);
    }
    
    if (options.outputFile) {
      try {
        await writeFile(options.outputFile, xml, 'utf8');
        console.log(`XML written to '${options.outputFile}'`);
      } catch (error) {
        console.error(`Error writing to file '${options.outputFile}': ${error.message}`);
        process.exit(1);
      }
    } else {
      process.stdout.write(xml);
    }
    
  } catch (error) {
    console.error(`Unexpected error: ${error.message}`);
    process.exit(1);
  }
}

main();
