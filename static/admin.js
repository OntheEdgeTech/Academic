// Keep track of whether the markdown editor is already initialized
let markdownEditorInitialized = false;

// Define all markdown editor functions in global scope
function initMarkdownEditor() {
    // Check if required elements exist
    const editorTextarea = document.getElementById('document-content');
    const editorPreview = document.getElementById('editor-preview');
    const previewToggle = document.getElementById('preview-toggle');

    if (!editorTextarea || !editorPreview || !previewToggle) {
        console.warn('Markdown editor elements not found, skipping initialization');
        return;
    }

    // If already initialized, don't do it again
    if (markdownEditorInitialized) {
        return;
    }

    // Mark as initialized
    markdownEditorInitialized = true;

    // Add event listeners for editor buttons
    function editorClickHandler(e) {
        // Handle editor button clicks
        if (e.target.matches('.editor-btn') || e.target.closest('.editor-btn')) {
            e.preventDefault();
            const button = e.target.matches('.editor-btn') ? e.target : e.target.closest('.editor-btn');
            const command = button.getAttribute('data-command');
            if (command) {
                handleEditorCommand(command);
            }
        }
    }

    // Remove any existing listener and add the new one
    document.removeEventListener('click', editorClickHandler, true);
    document.addEventListener('click', editorClickHandler, true);

    // Handle preview toggle separately
    function previewToggleHandler(e) {
        e.preventDefault();
        togglePreview();
    }

    // Handle edit toggle separately
    function editToggleHandler(e) {
        e.preventDefault();
        togglePreview();
    }

    // Remove any existing listener and add the new one
    previewToggle.removeEventListener('click', previewToggleHandler);
    previewToggle.addEventListener('click', previewToggleHandler);

    // Remove any existing listener and add the new one for edit button
    const editToggle = document.getElementById('edit-toggle');
    if (editToggle) {
        editToggle.removeEventListener('click', editToggleHandler);
        editToggle.addEventListener('click', editToggleHandler);
    }

    // Handle keyboard shortcuts
    function keydownHandler(e) {
        // Ctrl+B for bold
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            handleEditorCommand('bold');
        }
        // Ctrl+I for italic
        else if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
            e.preventDefault();
            handleEditorCommand('italic');
        }
        // Ctrl+H for heading
        else if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
            e.preventDefault();
            handleEditorCommand('heading');
        }
        // Ctrl+K for link
        else if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            handleEditorCommand('link');
        }
    }

    // Remove any existing listener and add the new one
    editorTextarea.removeEventListener('keydown', keydownHandler);
    editorTextarea.addEventListener('keydown', keydownHandler);

    // Handle edit document button in footer
    const editDocumentBtn = document.getElementById('edit-document-btn');
    if (editDocumentBtn) {
        function editDocumentHandler(e) {
            e.preventDefault();
            togglePreview();
        }

        // Remove any existing listener and add the new one
        editDocumentBtn.removeEventListener('click', editDocumentHandler);
        editDocumentBtn.addEventListener('click', editDocumentHandler);
    }
}

function handleEditorCommand(command) {
    const editor = document.getElementById('document-content');
    if (!editor) return;

    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const selectedText = editor.value.substring(start, end);
    let newText = '';
    let cursorPos = start;

    switch (command) {
        case 'bold':
            newText = `**${selectedText}**`;
            cursorPos = start + 2;
            break;
        case 'italic':
            newText = `*${selectedText}*`;
            cursorPos = start + 1;
            break;
        case 'heading':
            newText = `# ${selectedText}`;
            cursorPos = start + 2;
            break;
        case 'link':
            newText = `[${selectedText}](url)`;
            cursorPos = start + selectedText.length + 3;
            break;
        case 'image':
            newText = `![alt text](image-url)`;
            cursorPos = start + 2;
            break;
        case 'code':
            newText = '```\n' + selectedText + '\n```';
            cursorPos = start + 4;
            break;
        case 'quote':
            newText = `> ${selectedText}`;
            cursorPos = start + 2;
            break;
        case 'list-ul':
            newText = selectedText.split('\n').map(line => `- ${line}`).join('\n');
            cursorPos = start + 2;
            break;
        case 'list-ol':
            const lines = selectedText.split('\n');
            newText = lines.map((line, i) => `${i + 1}. ${line}`).join('\n');
            cursorPos = start + 3;
            break;
        case 'hr':
            newText = `${selectedText}\n\n---\n\n`;
            cursorPos = start + selectedText.length + 6;
            break;
    }

    // Update textarea
    editor.value = editor.value.substring(0, start) + newText + editor.value.substring(end);

    // Set cursor position
    editor.focus();
    editor.setSelectionRange(cursorPos, cursorPos + selectedText.length);
}

function togglePreview() {
    const editorPreview = document.getElementById('editor-preview');
    const editorTextarea = document.getElementById('document-content');
    const previewToggle = document.getElementById('preview-toggle');
    const editToggle = document.getElementById('edit-toggle');
    const editDocumentBtn = document.getElementById('edit-document-btn');
    const editorToolbar = document.querySelector('.editor-toolbar');

    if (editorPreview && editorTextarea && previewToggle && editToggle) {
        const isPreviewActive = editorPreview.classList.contains('active');
        if (isPreviewActive) {
            // Switch to editor
            editorPreview.classList.remove('active');
            editorTextarea.style.display = 'block';
            previewToggle.style.display = 'inline-block';
            editToggle.style.display = 'none';
            // Hide the edit document button in footer when in edit mode
            if (editDocumentBtn) {
                editDocumentBtn.style.display = 'none';
            }
            // Show toolbar when in edit mode
            if (editorToolbar) {
                editorToolbar.style.display = 'flex';
            }
        } else {
            // Switch to preview
            if (typeof markdownit !== 'undefined') {
                const md = markdownit({
                    html: false,
                    xhtmlOut: false,
                    breaks: true,
                    linkify: true,
                    typographer: true
                });
                editorPreview.innerHTML = '<div class="editor-preview-content">' +
                    md.render(editorTextarea.value) + '</div>';
            } else {
                // Fallback to escaped HTML
                const escapeHtml = (text) => {
                    const div = document.createElement('div');
                    div.textContent = text;
                    return div.innerHTML;
                };
                editorPreview.innerHTML = '<div class="editor-preview-content">' +
                    '<p>Markdown preview requires additional library.</p>' +
                    '<p>Please add markdown-it library to enable preview.</p>' +
                    '<pre>' + escapeHtml(editorTextarea.value) + '</pre>' +
                    '</div>';
            }
            editorPreview.classList.add('active');
            editorTextarea.style.display = 'none';
            previewToggle.style.display = 'none';
            editToggle.style.display = 'inline-block';
            // Show the edit document button in footer when in preview mode
            if (editDocumentBtn) {
                editDocumentBtn.style.display = 'inline-block';
            }
            // Hide toolbar when in preview mode
            if (editorToolbar) {
                editorToolbar.style.display = 'none';
            }
        }
    }
}

// Admin Panel Functionality
document.addEventListener('DOMContentLoaded', function () {
    // Tab switching
    const tabItems = document.querySelectorAll('.admin-sidebar-nav-item');
    const tabContents = document.querySelectorAll('.admin-tab-content');

    tabItems.forEach(item => {
        item.addEventListener('click', function () {
            const tabName = this.getAttribute('data-tab');

            // Update active tab
            tabItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            // Show active content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabName + '-tab') {
                    content.classList.add('active');
                }
            });
        });
    });

    // Modal functionality
    const modals = document.querySelectorAll('.admin-modal');
    const closeButtons = document.querySelectorAll('.admin-modal-close');
    const cancelButtons = document.querySelectorAll('[id$="-modal-close"]');

    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const modal = this.closest('.admin-modal');
            modal.style.display = 'none';
            // Reset markdown editor initialization when document modal is closed
            if (modal.id === 'document-modal') {
                markdownEditorInitialized = false;
            }
        });
    });

    cancelButtons.forEach(button => {
        button.addEventListener('click', function () {
            const modal = this.closest('.admin-modal');
            modal.style.display = 'none';
            // Reset markdown editor initialization when document modal is closed
            if (modal.id === 'document-modal') {
                markdownEditorInitialized = false;
            }
        });
    });

    window.addEventListener('click', function (event) {
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
                // Reset markdown editor initialization when document modal is closed
                if (modal.id === 'document-modal') {
                    markdownEditorInitialized = false;
                }
            }
        });
    });

    // Markdown Editor Functionality
    // (All functions moved to global scope above)

    function handleEditorCommand(command) {
        const editor = document.getElementById('document-content');
        if (!editor) return;

        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        const selectedText = editor.value.substring(start, end);
        let newText = '';
        let cursorPos = start;

        switch (command) {
            case 'bold':
                newText = `**${selectedText}**`;
                cursorPos = start + 2;
                break;
            case 'italic':
                newText = `*${selectedText}*`;
                cursorPos = start + 1;
                break;
            case 'heading':
                newText = `# ${selectedText}`;
                cursorPos = start + 2;
                break;
            case 'link':
                newText = `[${selectedText}](url)`;
                cursorPos = start + selectedText.length + 3;
                break;
            case 'image':
                newText = `![alt text](image-url)`;
                cursorPos = start + 2;
                break;
            case 'code':
                newText = '```\n' + selectedText + '\n```';
                cursorPos = start + 4;
                break;
            case 'quote':
                newText = `> ${selectedText}`;
                cursorPos = start + 2;
                break;
            case 'list-ul':
                newText = selectedText.split('\n').map(line => `- ${line}`).join('\n');
                cursorPos = start + 2;
                break;
            case 'list-ol':
                const lines = selectedText.split('\n');
                newText = lines.map((line, i) => `${i + 1}. ${line}`).join('\n');
                cursorPos = start + 3;
                break;
            case 'hr':
                newText = `${selectedText}\n\n---\n\n`;
                cursorPos = start + selectedText.length + 6;
                break;
        }

        // Update textarea
        editor.value = editor.value.substring(0, start) + newText + editor.value.substring(end);

        // Set cursor position
        editor.focus();
        editor.setSelectionRange(cursorPos, cursorPos + selectedText.length);
    }

    function togglePreview() {
        const editorPreview = document.getElementById('editor-preview');
        const editorTextarea = document.getElementById('document-content');
        const previewToggle = document.getElementById('preview-toggle');
        const editToggle = document.getElementById('edit-toggle');
        const editorToolbar = document.querySelector('.editor-toolbar');

        if (editorPreview && editorTextarea && previewToggle && editToggle) {
            const isPreviewActive = editorPreview.classList.contains('active');
            if (isPreviewActive) {
                // Switch to editor
                editorPreview.classList.remove('active');
                editorTextarea.style.display = 'block';
                previewToggle.style.display = 'inline-block';
                editToggle.style.display = 'none';
                // Show toolbar when in edit mode
                if (editorToolbar) {
                    editorToolbar.style.display = 'flex';
                }
            } else {
                // Switch to preview
                if (typeof markdownit !== 'undefined') {
                    const md = markdownit({
                        html: false,
                        xhtmlOut: false,
                        breaks: true,
                        linkify: true,
                        typographer: true
                    });
                    editorPreview.innerHTML = '<div class="editor-preview-content">' +
                        md.render(editorTextarea.value) + '</div>';
                } else {
                    // Fallback to escaped HTML
                    const escapeHtml = (text) => {
                        const div = document.createElement('div');
                        div.textContent = text;
                        return div.innerHTML;
                    };
                    editorPreview.innerHTML = '<div class="editor-preview-content">' +
                        '<p>Markdown preview requires additional library.</p>' +
                        '<p>Please add markdown-it library to enable preview.</p>' +
                        '<pre>' + escapeHtml(editorTextarea.value) + '</pre>' +
                        '</div>';
                }
                editorPreview.classList.add('active');
                editorTextarea.style.display = 'none';
                previewToggle.style.display = 'none';
                editToggle.style.display = 'inline-block';
                // Hide toolbar when in preview mode
                if (editorToolbar) {
                    editorToolbar.style.display = 'none';
                }
            }
        }
    }

    // Initialize markdown editor when document modal is shown
    function setupDocumentModalObserver() {
        const documentModal = document.getElementById('document-modal');
        if (documentModal) {
            const observer = new MutationObserver(function (mutations) {
                mutations.forEach(function (mutation) {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                        if (documentModal.style.display === 'flex') {
                            // Small delay to ensure DOM is fully rendered
                            setTimeout(initMarkdownEditor, 100);
                        }
                    }
                });
            });

            observer.observe(documentModal, {
                attributes: true,
                attributeFilter: ['style']
            });
        }
    }

    // Set up the observer
    setupDocumentModalObserver();

    // Also initialize when showing the modal directly
    document.getElementById('new-document-btn').addEventListener('click', function () {
        if (!documentCourseSelector.value) return;

        document.getElementById('document-modal-title').textContent = 'Add New Document';
        document.getElementById('document-form').reset();
        document.getElementById('document-id').value = '';
        document.getElementById('document-course').value = documentCourseSelector.value;
        document.getElementById('document-modal').style.display = 'flex';
        // Reset and initialize the editor
        markdownEditorInitialized = false;
        setTimeout(initMarkdownEditor, 100);
    });

    // Initialize when editing a document
    function setupEditDocumentButtons() {
        document.querySelectorAll('.edit-doc').forEach(button => {
            button.addEventListener('click', function () {
                // We need to reattach the event listeners after the modal is populated
                setTimeout(initMarkdownEditor, 100);
            });
        });
    }

    // Course search
    const courseSearch = document.getElementById('course-search');
    if (courseSearch) {
        courseSearch.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#courses-table-body tr');

            rows.forEach(row => {
                const courseName = row.cells[0].textContent.toLowerCase();
                const description = row.cells[1].textContent.toLowerCase();

                if (courseName.includes(searchTerm) || description.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Document search
    const documentSearch = document.getElementById('document-search');
    if (documentSearch) {
        documentSearch.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#documents-table-body tr');

            rows.forEach(row => {
                if (row.cells) {
                    const docName = row.cells[0].textContent.toLowerCase();
                    if (docName.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                }
            });
        });
    }

    // Course selector for documents
    const documentCourseSelector = document.getElementById('document-course-selector');
    const newDocumentBtn = document.getElementById('new-document-btn');

    documentCourseSelector.addEventListener('change', function () {
        newDocumentBtn.disabled = !this.value;
        if (this.value) {
            loadDocuments(this.value);
        } else {
            document.getElementById('documents-table-body').innerHTML =
                '<tr><td colspan="4" class="text-center">Select a course to view documents</td></tr>';
        }
    });

    // Button actions
    document.getElementById('new-course-btn').addEventListener('click', function () {
        document.getElementById('course-modal-title').textContent = 'Add New Course';
        document.getElementById('course-form').reset();
        document.getElementById('course-id').value = '';
        document.getElementById('course-modal').style.display = 'flex';
    });

    document.getElementById('new-course-action').addEventListener('click', function () {
        document.querySelector('.admin-sidebar-nav-item[data-tab="courses"]').click();
        document.getElementById('new-course-btn').click();
    });

    document.getElementById('manage-courses-action').addEventListener('click', function () {
        document.querySelector('.admin-sidebar-nav-item[data-tab="courses"]').click();
    });

    document.getElementById('new-document-btn').addEventListener('click', function () {
        if (!documentCourseSelector.value) return;

        document.getElementById('document-modal-title').textContent = 'Add New Document';
        document.getElementById('document-form').reset();
        document.getElementById('document-id').value = '';
        document.getElementById('document-course').value = documentCourseSelector.value;
        document.getElementById('document-modal').style.display = 'flex';
        initMarkdownEditor(); // Initialize when showing the modal
    });

    // Edit course buttons
    document.querySelectorAll('.edit-course').forEach(button => {
        button.addEventListener('click', function () {
            const courseName = this.getAttribute('data-name');

            // Switch to courses tab
            document.querySelector('.admin-sidebar-nav-item[data-tab="courses"]').click();

            // Fill form
            document.getElementById('course-modal-title').textContent = 'Edit Course';
            document.getElementById('course-name').value = courseName;
            document.getElementById('course-id').value = courseName;

            // Try to get description
            fetch('/api/courses')
                .then(response => response.json())
                .then(courses => {
                    const course = courses.find(c => c.name === courseName);
                    if (course) {
                        document.getElementById('course-description').value = course.description || '';
                    }
                });

            document.getElementById('course-modal').style.display = 'flex';
        });
    });

    // Delete course buttons
    document.querySelectorAll('.delete-course').forEach(button => {
        button.addEventListener('click', function () {
            const courseName = this.getAttribute('data-name');

            if (confirm(`Are you sure you want to delete the course "${courseName}" and all its documents?`)) {
                fetch(`/api/courses/${encodeURIComponent(courseName)}`, {
                    method: 'DELETE'
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.message) {
                            // Remove row from table
                            document.querySelector(`tr[data-course="${courseName}"]`).remove();
                            updateStats();
                            showToast('Course deleted successfully', 'success');
                        } else {
                            showToast('Error: ' + (data.error || 'Could not delete course'), 'error');
                        }
                    })
                    .catch(error => {
                        showToast('Error: ' + error.message, 'error');
                    });
            }
        });
    });

    // Manage documents buttons
    document.querySelectorAll('.manage-docs').forEach(button => {
        button.addEventListener('click', function () {
            const courseName = this.getAttribute('data-name');

            // Switch to documents tab
            document.querySelector('.admin-sidebar-nav-item[data-tab="documents"]').click();

            // Set course selector
            documentCourseSelector.value = courseName;
            newDocumentBtn.disabled = false;

            // Load documents
            loadDocuments(courseName);
        });
    });

    // Save course
    document.getElementById('course-modal-save').addEventListener('click', function () {
        const courseName = document.getElementById('course-name').value;
        const description = document.getElementById('course-description').value;
        const courseId = document.getElementById('course-id').value;

        if (!courseName) {
            showToast('Course name is required', 'error');
            return;
        }

        const isUpdate = !!courseId && courseId !== courseName;

        if (isUpdate) {
            if (confirm(`This will delete the course "${courseId}" and create a new course "${courseName}". Continue?`)) {
                // Delete old course
                fetch(`/api/courses/${encodeURIComponent(courseId)}`, {
                    method: 'DELETE'
                })
                    .then(response => {
                        if (response.ok) {
                            // Create new course
                            return fetch('/api/courses', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    name: courseName,
                                    description: description
                                })
                            });
                        } else {
                            throw new Error('Failed to delete old course');
                        }
                    })
                    .then(response => response.json())
                    .then(result => {
                        if (result.message) {
                            location.reload();
                        } else {
                            showToast('Error: ' + (result.error || 'Could not update course'), 'error');
                        }
                    })
                    .catch(error => {
                        showToast('Error: ' + error.message, 'error');
                    });
            }
        } else {
            // Create new course
            fetch('/api/courses', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: courseName,
                    description: description
                })
            })
                .then(response => response.json())
                .then(result => {
                    if (result.message) {
                        location.reload();
                    } else {
                        showToast('Error: ' + (result.error || 'Could not create course'), 'error');
                    }
                })
                .catch(error => {
                    showToast('Error: ' + error.message, 'error');
                });
        }
    });

    // Save document
    document.getElementById('document-modal-save').addEventListener('click', function () {
        const documentName = document.getElementById('document-name').value;
        const content = document.getElementById('document-content').value;
        const courseName = document.getElementById('document-course').value;

        if (!documentName || !content || !courseName) {
            showToast('All fields are required', 'error');
            return;
        }

        // Ensure .md extension
        const filename = documentName.endsWith('.md') ? documentName : documentName + '.md';

        fetch(`/api/courses/${encodeURIComponent(courseName)}/documents`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: filename,
                content: content
            })
        })
            .then(response => response.json())
            .then(result => {
                if (result.message) {
                    document.getElementById('document-modal').style.display = 'none';
                    markdownEditorInitialized = false; // Reset initialization flag
                    loadDocuments(courseName);
                    showToast('Document saved successfully', 'success');
                } else {
                    showToast('Error: ' + (result.error || 'Could not save document'), 'error');
                }
            })
            .catch(error => {
                showToast('Error: ' + error.message, 'error');
            });
    });

    // Load documents for a course
    function loadDocuments(courseName) {
        // Show loading spinner
        document.getElementById('documents-table-body').innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center">
                            <div class="loading-spinner" style="margin: 20px auto;"></div>
                        </td>
                    </tr>
                `;

        fetch(`/api/courses/${encodeURIComponent(courseName)}/documents`)
            .then(response => response.json())
            .then(documents => {
                const tbody = document.getElementById('documents-table-body');

                if (documents.length > 0) {
                    let html = '';
                    documents.forEach(doc => {
                        const filename = doc.filename.replace(/\.md$/, '');
                        html += `
                            <tr>
                                <td>${filename}</td>
                                <td>${courseName}</td>
                                <td>Just now</td>
                                <td>
                                    <div class="admin-table-actions">
                                        <button class="admin-btn admin-btn-sm admin-btn-secondary edit-doc" data-filename="${doc.filename}" data-course="${courseName}">
                                            <i>✏️</i> Edit
                                        </button>
                                        <button class="admin-btn admin-btn-sm admin-btn-danger delete-doc" data-filename="${doc.filename}" data-course="${courseName}">
                                            <i>🗑️</i> Delete
                                        </button>
                                    </div>
                                </td>
                            </tr>`;
                    });
                    tbody.innerHTML = html;

                    // Add event listeners
                    tbody.querySelectorAll('.edit-doc').forEach(button => {
                        button.addEventListener('click', function () {
                            const filename = this.getAttribute('data-filename');
                            const course = this.getAttribute('data-course');
                            editDocument(course, filename);
                        });
                    });

                    tbody.querySelectorAll('.delete-doc').forEach(button => {
                        button.addEventListener('click', function () {
                            const filename = this.getAttribute('data-filename');
                            const course = this.getAttribute('data-course');
                            deleteDocument(course, filename);
                        });
                    });

                    // Initialize markdown editor for edit buttons
                    setupEditDocumentButtons();
                } else {
                    tbody.innerHTML = '<tr><td colspan="4" class="text-center">No documents found</td></tr>';
                }
            })
            .catch(error => {
                document.getElementById('documents-table-body').innerHTML =
                    '<tr><td colspan="4" class="text-center">Error loading documents</td></tr>';
                showToast('Error loading documents: ' + error.message, 'error');
            });
    }

    // Edit document
    function editDocument(courseName, filename) {
        fetch(`/api/courses/${encodeURIComponent(courseName)}/documents/${encodeURIComponent(filename)}`)
            .then(response => response.json())
            .then(doc => {
                if (doc.content !== undefined) {
                    document.getElementById('document-modal-title').textContent = 'Edit Document';
                    document.getElementById('document-name').value = filename.replace(/\.md$/, '');
                    document.getElementById('document-content').value = doc.content;
                    document.getElementById('document-id').value = filename;
                    document.getElementById('document-course').value = courseName;
                    document.getElementById('document-modal').style.display = 'flex';
                    // Reset and initialize the editor
                    markdownEditorInitialized = false;
                    setTimeout(initMarkdownEditor, 100);
                } else {
                    showToast('Error loading document', 'error');
                }
            })
            .catch(error => {
                showToast('Error loading document: ' + error.message, 'error');
            });
    }

    // Delete document
    function deleteDocument(courseName, filename) {
        if (confirm(`Are you sure you want to delete the document "${filename}"?`)) {
            fetch(`/api/courses/${encodeURIComponent(courseName)}/documents/${encodeURIComponent(filename)}`, {
                method: 'DELETE'
            })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        loadDocuments(courseName);
                        showToast('Document deleted successfully', 'success');
                    } else {
                        showToast('Error: ' + (data.error || 'Could not delete document'), 'error');
                    }
                })
                .catch(error => {
                    showToast('Error: ' + error.message, 'error');
                });
        }
    }

    // Update stats
    function updateStats() {
        // In a real implementation, you would update the stats dynamically
        // For now, we rely on the server-side rendering
    }

    // Drag and drop functionality for courses
    const coursesTable = document.getElementById('courses-table-body');
    if (coursesTable) {
        let draggedRow = null;

        coursesTable.addEventListener('dragstart', function (e) {
            if (e.target.classList.contains('draggable-course')) {
                draggedRow = e.target;
                e.target.style.opacity = '0.5';
            }
        });

        coursesTable.addEventListener('dragend', function (e) {
            if (e.target.classList.contains('draggable-course')) {
                e.target.style.opacity = '1';
                draggedRow = null;
            }
        });

        coursesTable.addEventListener('dragover', function (e) {
            e.preventDefault();
        });

        coursesTable.addEventListener('dragenter', function (e) {
            if (e.target.classList.contains('draggable-course') && e.target !== draggedRow) {
                e.target.style.backgroundColor = 'var(--tertiary-bg)';
            }
        });

        coursesTable.addEventListener('dragleave', function (e) {
            if (e.target.classList.contains('draggable-course')) {
                e.target.style.backgroundColor = '';
            }
        });

        coursesTable.addEventListener('drop', function (e) {
            e.preventDefault();
            if (e.target.classList.contains('draggable-course') && draggedRow) {
                e.target.style.backgroundColor = '';
                // In a real implementation, you would send a request to reorder courses
                showToast('Course order updated', 'success');
            }
        });
    }

    // Drag and drop for document import
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const browseFilesBtn = document.getElementById('browse-files');
    const importProgress = document.getElementById('import-progress');

    if (dropArea && fileInput && browseFilesBtn) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        dropArea.addEventListener('drop', handleDrop, false);

        // Handle file selection via button
        browseFilesBtn.addEventListener('click', function () {
            fileInput.click();
        });

        fileInput.addEventListener('change', function () {
            handleFiles(this.files);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        function highlight() {
            dropArea.style.backgroundColor = 'var(--tertiary-bg)';
            dropArea.style.borderColor = 'var(--accent-secondary)';
        }

        function unhighlight() {
            dropArea.style.backgroundColor = '';
            dropArea.style.borderColor = '';
        }

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        function handleFiles(files) {
            if (files.length === 0) return;

            // Show progress indicator
            importProgress.style.display = 'block';

            // In a real implementation, you would upload and process the files
            // For now, we'll just simulate the process
            setTimeout(() => {
                importProgress.style.display = 'none';
                showToast(`${files.length} document(s) imported successfully`, 'success');
            }, 2000);
        }
    }
});

// Toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') ||
        (() => {
            const container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
            return container;
        })();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';

    toast.innerHTML = `
                <span class="toast-icon">${icon}</span>
                <div class="toast-content">${message}</div>
                <button class="toast-close">&times;</button>
            `;

    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });

    toastContainer.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

// Initialize markdown editor when document modal is shown
function initMarkdownEditorOnModalShow() {
    const documentModal = document.getElementById('document-modal');
    if (documentModal) {
        const observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    if (documentModal.style.display === 'flex') {
                        // Small delay to ensure DOM is fully rendered
                        setTimeout(initMarkdownEditor, 100);
                    }
                }
            });
        });

        observer.observe(documentModal, {
            attributes: true,
            attributeFilter: ['style']
        });
    }
}

// Call this function to set up the observer
initMarkdownEditorOnModalShow();