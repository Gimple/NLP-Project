// DOM Elements
const imageContainer = document.getElementById('image-container');
const placeholder = document.getElementById('placeholder');
const previewImage = document.getElementById('preview-image');
const pasteBtn = document.getElementById('paste-btn');
const openBtn = document.getElementById('open-btn');
const clearBtn = document.getElementById('clear-btn');
const fileInput = document.getElementById('file-input');
const loadingIndicator = document.getElementById('loading-indicator');
const ocrOutput = document.getElementById('ocr-output');
const editableText = document.getElementById('editable-text');
const statusBar = document.getElementById('status-bar');

// Mode switching elements
const imageModeBtn = document.getElementById('image-mode-btn');
const urlModeBtn = document.getElementById('url-mode-btn');
const imagePanel = document.getElementById('image-panel');
const urlPanel = document.getElementById('url-panel');

// URL analysis elements
const urlInput = document.getElementById('url-input');
const analyzeUrlBtn = document.getElementById('analyze-url-btn');
const clearUrlBtn = document.getElementById('clear-url-btn');
const articleInfo = document.getElementById('article-info');

// State
let currentImage = null;
let currentMode = 'image'; // 'image' or 'url'

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateStatus('Ready');
});

function initializeEventListeners() {
    // Mode switching
    imageModeBtn.addEventListener('click', () => switchMode('image'));
    urlModeBtn.addEventListener('click', () => switchMode('url'));
    
    // URL analysis
    analyzeUrlBtn.addEventListener('click', analyzeUrl);
    clearUrlBtn.addEventListener('click', clearUrlAnalysis);
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            analyzeUrl();
        }
    });

    // Button event listeners
    pasteBtn.addEventListener('click', pasteImage);
    openBtn.addEventListener('click', () => fileInput.click());
    clearBtn.addEventListener('click', clearAll);
    fileInput.addEventListener('change', handleFileSelect);

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeydown);

    // Drag and drop
    imageContainer.addEventListener('dragover', handleDragOver);
    imageContainer.addEventListener('dragleave', handleDragLeave);
    imageContainer.addEventListener('drop', handleDrop);

    // Paste event
    document.addEventListener('paste', handlePaste);
}

function handleKeydown(event) {
    if (event.ctrlKey && event.key === 'v') {
        event.preventDefault();
        pasteImage();
    }
}

function handleDragOver(event) {
    event.preventDefault();
    imageContainer.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.preventDefault();
    imageContainer.classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    imageContainer.classList.remove('drag-over');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (isValidImageFile(file)) {
            processFile(file);
        } else {
            showError('Please drop a valid image file (PNG, JPG, JPEG, BMP, TIF, TIFF)');
        }
    }
}

function handlePaste(event) {
    const items = event.clipboardData.items;
    
    for (let item of items) {
        if (item.type.indexOf('image') !== -1) {
            event.preventDefault();
            const file = item.getAsFile();
            processFile(file);
            return;
        }
    }
}

function pasteImage() {
    // Try to access clipboard using the Clipboard API
    if (navigator.clipboard && navigator.clipboard.read) {
        navigator.clipboard.read().then(clipboardItems => {
            for (const clipboardItem of clipboardItems) {
                for (const type of clipboardItem.types) {
                    if (type.startsWith('image/')) {
                        clipboardItem.getType(type).then(blob => {
                            processFile(blob);
                        });
                        return;
                    }
                }
            }
            showError('No image found in clipboard. Try using Windows+Shift+S to take a screenshot and then paste.');
        }).catch(err => {
            showError('Unable to access clipboard. Please use Ctrl+V or drag and drop an image file.');
        });
    } else {
        showError('Clipboard access not supported. Please drag and drop an image file or use the Open File button.');
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file && isValidImageFile(file)) {
        processFile(file);
    }
}

function isValidImageFile(file) {
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff', 'image/tif'];
    return allowedTypes.includes(file.type);
}

function processFile(file) {
    if (!isValidImageFile(file)) {
        showError('Invalid file type. Please select an image file (PNG, JPG, JPEG, BMP, TIF, TIFF)');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        displayImage(e.target.result);
        processImageWithOCR(e.target.result);
    };
    reader.readAsDataURL(file);
}

function displayImage(imageSrc) {
    currentImage = imageSrc;
    placeholder.style.display = 'none';
    previewImage.src = imageSrc;
    previewImage.style.display = 'block';
    updateStatus('Image loaded');
}

function processImageWithOCR(imageData) {
    showLoading(true);
    updateStatus('Processing image...');
    
    // Clear previous results
    ocrOutput.value = '';
    editableText.value = '';

    // Send image to Flask backend
    fetch('/process_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image: imageData
        })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success) {
            // Display OCR results
            const ocrResult = `--- OCR Output ---\n${data.raw_text}\n\n--- Cleaned Output ---\n${data.cleaned_text}`;
            ocrOutput.value = ocrResult;
            editableText.value = data.cleaned_text;
            updateStatus('OCR processing completed');
            showSuccess('Text extraction completed successfully!');
        } else {
            showError(data.error || 'OCR processing failed');
            updateStatus('OCR processing failed');
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Error:', error);
        showError('Network error occurred while processing image');
        updateStatus('Network error');
    });
}

function clearAll() {
    currentImage = null;
    placeholder.style.display = 'block';
    previewImage.style.display = 'none';
    previewImage.src = '';
    ocrOutput.value = '';
    editableText.value = '';
    fileInput.value = '';
    showLoading(false);
    updateStatus('Ready - All content cleared');
    clearMessages();
}

function showLoading(show) {
    if (show) {
        loadingIndicator.style.display = 'block';
        // Disable buttons during processing
        pasteBtn.disabled = true;
        openBtn.disabled = true;
        clearBtn.disabled = true;
    } else {
        loadingIndicator.style.display = 'none';
        // Re-enable buttons
        pasteBtn.disabled = false;
        openBtn.disabled = false;
        clearBtn.disabled = false;
    }
}

function updateStatus(message) {
    statusBar.textContent = message;
}

function showError(message) {
    clearMessages();
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message error';
    errorDiv.textContent = message;
    
    // Insert after the button panel
    const buttonPanel = document.querySelector('.button-panel');
    buttonPanel.parentNode.insertBefore(errorDiv, buttonPanel.nextSibling);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

function showSuccess(message) {
    clearMessages();
    const successDiv = document.createElement('div');
    successDiv.className = 'message success';
    successDiv.textContent = message;
    
    // Insert after the button panel
    const buttonPanel = document.querySelector('.button-panel');
    buttonPanel.parentNode.insertBefore(successDiv, buttonPanel.nextSibling);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.parentNode.removeChild(successDiv);
        }
    }, 3000);
}

function clearMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        if (message.parentNode) {
            message.parentNode.removeChild(message);
        }
    });
}

// File upload via form (alternative method)
function uploadFile() {
    const formData = new FormData();
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a file first');
        return;
    }
    
    formData.append('file', file);
    
    showLoading(true);
    updateStatus('Uploading and processing...');
    
    fetch('/process_file', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success) {
            const ocrResult = `--- OCR Output ---\n${data.raw_text}\n\n--- Cleaned Output ---\n${data.cleaned_text}`;
            ocrOutput.value = ocrResult;
            editableText.value = data.cleaned_text;
            updateStatus('File processing completed');
            showSuccess('Text extraction completed successfully!');
        } else {
            showError(data.error || 'File processing failed');
            updateStatus('File processing failed');
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Error:', error);
        showError('Network error occurred while processing file');
        updateStatus('Network error');
    });
}

// Mode switching functionality
function switchMode(mode) {
    currentMode = mode;
    
    if (mode === 'image') {
        // Switch to image mode
        imageModeBtn.classList.add('active');
        urlModeBtn.classList.remove('active');
        imagePanel.style.display = 'block';
        urlPanel.style.display = 'none';
        updateStatus('Image Analysis Mode - Ready');
    } else if (mode === 'url') {
        // Switch to URL mode
        urlModeBtn.classList.add('active');
        imageModeBtn.classList.remove('active');
        urlPanel.style.display = 'block';
        imagePanel.style.display = 'none';
        updateStatus('URL Analysis Mode - Ready');
        
        // Clear previous URL analysis results
        clearUrlAnalysis();
    }
}

// URL Analysis functionality
function analyzeUrl() {
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Please enter a URL');
        return;
    }
    
    if (!isValidUrl(url)) {
        showError('Please enter a valid URL (must start with http:// or https://)');
        return;
    }
    
    // Hide article info initially
    articleInfo.style.display = 'none';
    
    // Clear text areas
    ocrOutput.value = '';
    editableText.value = '';
    
    // Disable analyze button
    analyzeUrlBtn.disabled = true;
    analyzeUrlBtn.textContent = 'Analyzing...';
    
    updateStatus('Processing URL...');
    
    // Process URL directly
    processUrl(url);
}

function isValidUrl(string) {
    try {
        new URL(string);
        return string.startsWith('http://') || string.startsWith('https://');
    } catch (_) {
        return false;
    }
}

function processUrl(url) {
    fetch('/process_url', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Display results
            displayUrlResults(data);
            
            // Re-enable analyze button
            analyzeUrlBtn.disabled = false;
            analyzeUrlBtn.textContent = 'Analyze';
            
            updateStatus('URL analysis completed successfully');
            showSuccess('Article analysis completed!');
        } else {
            // Handle error
            analyzeUrlBtn.disabled = false;
            analyzeUrlBtn.textContent = 'Analyze';
            updateStatus('URL analysis failed');
            showError(data.error || 'Failed to process URL');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        analyzeUrlBtn.disabled = false;
        analyzeUrlBtn.textContent = 'Analyze';
        updateStatus('Network error');
        showError('Network error occurred while processing URL');
    });
}


function displayUrlResults(data) {
    // Show article info
    articleInfo.style.display = 'block';
    
    // Update article information
    document.getElementById('article-title').textContent = data.article.title || 'No title found';
    document.getElementById('article-source').textContent = data.article.source || 'Unknown source';
    document.getElementById('article-url').textContent = data.article.url || '';
    
    // Display extracted and cleaned text
    const combinedText = `--- Article Title ---\n${data.article.title || 'No title'}\n\n--- Raw Content ---\n${data.article.content || 'No content extracted'}\n\n--- Cleaned Content ---\n${data.cleaned_text || 'No cleaned text'}`;
    
    ocrOutput.value = combinedText;
    editableText.value = data.cleaned_text || '';
}

function clearUrlAnalysis() {
    // Clear URL input and results
    urlInput.value = '';
    articleInfo.style.display = 'none';
    
    // Clear text areas
    ocrOutput.value = '';
    editableText.value = '';
    
    // Reset button state
    analyzeUrlBtn.disabled = false;
    analyzeUrlBtn.textContent = 'Analyze';
    
    // Update status
    updateStatus('URL Analysis Mode - Ready');
    
    // Clear any messages
    clearMessages();
}
