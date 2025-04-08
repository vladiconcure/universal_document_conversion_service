import uno
from os.path import abspath
import sys
import logging
import time

logger = logging.getLogger(__name__)

def path_to_url(path):
    """Convert a system path to a LibreOffice URL"""
    return uno.systemPathToFileUrl(abspath(path))

def connect_to_libreoffice(host="localhost", port=2002, max_retries=3):
    """Connect to a running LibreOffice instance with retry logic"""
    retries = 0
    while retries < max_retries:
        try:
            local_context = uno.getComponentContext()
            resolver = local_context.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", local_context
            )

            connection_string = f"uno:socket,host={host},port={port};urp;StarOffice.ComponentContext"
            logger.info(f"Connecting to LibreOffice with: {connection_string}")
            context = resolver.resolve(connection_string)
            
            logger.info("Successfully connected to LibreOffice")
            return context
        except Exception as e:
            retries += 1
            logger.warning(f"Connection attempt {retries}/{max_retries} failed: {e}")
            if retries >= max_retries:
                logger.error(f"Failed to connect to LibreOffice after {max_retries} attempts")
                raise
            time.sleep(1)  # Wait before retrying

def convert_document(input_path, output_path, export_filter, host="localhost", port=2002):
    """Convert a document from input_path to output_path using the specified export_filter"""
    try:
        # Connect to LibreOffice
        context = connect_to_libreoffice(host, port)
        smgr = context.ServiceManager
        
        # Create the Desktop instance
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", context)
        
        # Convert file paths to URLs
        input_url = path_to_url(input_path)
        output_url = path_to_url(output_path)
        
        # Set up document loading properties (hidden)
        hidden_prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        hidden_prop.Name = "Hidden"
        hidden_prop.Value = True
        
        readonly_prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        readonly_prop.Name = "ReadOnly"
        readonly_prop.Value = True
        
        load_props = (hidden_prop, readonly_prop)
        
        # Load the document
        logger.info(f"Loading document: {input_path}")
        document = desktop.loadComponentFromURL(input_url, "_blank", 0, load_props)
        if not document:
            raise Exception("Document failed to load")
        
        # Set up export properties
        export_prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        export_prop.Name = "FilterName"
        export_prop.Value = export_filter
        
        # For PDF, add additional options if needed
        if "pdf" in export_filter.lower():
            compression_prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
            compression_prop.Name = "CompressMode"
            compression_prop.Value = 1  # Best compression
            
            export_props = (export_prop, compression_prop)
        else:
            export_props = (export_prop,)
        
        # Export the document
        logger.info(f"Exporting document to: {output_path} with filter: {export_filter}")
        document.storeToURL(output_url, export_props)
        
        # Close the document
        document.close(True)
        logger.info("Document conversion completed successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error converting document: {e}")
        raise
