# Combined Documentation App

This application combines the best features of two documentation systems:
1. TechHandBook - Clean, modern documentation interface with excellent navigation
2. Welding Study App - Dynamic content management with admin panel

## Features

- **Modern UI**: Clean, dark-themed interface inspired by TechHandBook
- **File-based Documentation**: Organize content in courses with Markdown files
- **Admin Panel**: Full CRUD operations for managing courses and documents
- **Global Search**: Search across all courses and documents
- **Responsive Design**: Works on desktop and mobile devices
- **Markdown Support**: Full Markdown support with syntax highlighting
- **Navigation**: Previous/Next buttons, breadcrumbs, and table of contents
- **Course System**: Organize documentation into courses
- **Print Styles**: Optimized printing of documentation

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```

## Usage

1. **Browsing Documentation**: 
   - Visit the homepage to see available courses
   - Click on a course to start browsing documentation
   - Use the sidebar to navigate between documents
   - Use the search bar to find specific content across all courses
   - Table of contents is available on the right side of document pages

2. **Admin Panel**:
   - Visit `/login` to access the admin panel
   - Default credentials: admin / password123
   - Create, edit, and delete courses
   - Manage documents within courses
   - Preview Markdown content in real-time
   - Drag and drop to reorder courses
   - Bulk import documents via drag and drop

## Directory Structure

```
combined-docs-app/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── docs/               # File-based documentation (courses)
│   └── Welding 101/    # Sample course
│       ├── info.txt    # Course description
│       ├── 1. welcome.md
│       ├── 2. safety.md
│       └── 3. processes.md
├── media/              # Static media files
├── static/             # CSS and JavaScript files
│   ├── docs.css        # Main stylesheet
│   └── docs.js         # Client-side JavaScript
└── templates/          # HTML templates
    ├── docs.html       # Documentation page
    ├── landing.html    # Homepage
    ├── courses.html    # Courses listing
    ├── login.html      # Admin login
    └── admin.html      # Admin panel
```

## Technology Stack

- **Flask**: Python web framework
- **Markdown**: Content formatting
- **Fuse.js**: Client-side search
- **HTML/CSS/JavaScript**: Frontend

## Customization

You can customize the application by:

1. **Adding Courses**: Use the admin panel to create new courses
2. **Adding Documents**: Use the admin panel to add documents to courses
3. **Styling**: Modify `static/docs.css` to change the appearance
4. **Functionality**: Update `static/docs.js` for client-side enhancements
5. **Templates**: Modify HTML templates in the `templates/` directory

## Security Note

For production use, make sure to:
1. Change the secret key in `app.py`
2. Change the default admin credentials
3. Implement proper authentication and authorization

## UI Improvements

The UI has been significantly enhanced with:

### 1. Loading States
- Loading spinners for search results
- Skeleton screens when content is loading
- Progress indicators for long operations

### 2. Better Mobile Navigation
- Collapsible TOC on mobile with dedicated toggle button
- Improved touch targets for navigation
- Responsive design that adapts to all screen sizes

### 3. Enhanced Search Experience
- Real-time search with debouncing
- Search result highlighting
- Keyboard navigation for search results
- Search history and past searches functionality

### 4. Visual Feedback
- Toast notifications for actions
- Progress indicators for long operations
- Better error messaging with contextual information

### 5. Interactive Elements
- Code snippet copy buttons with visual feedback
- Expandable/collapsible sections
- Image lightbox for diagrams and screenshots
- Keyboard shortcuts for common actions

### 6. Navigation Enhancements
- Breadcrumb dropdown for quick course switching
- Recently viewed documents section
- Bookmark/favorite documents (stored in localStorage)

### 7. Content Presentation
- Dark-themed code blocks with syntax highlighting
- Math formula rendering (via extensions)
- Diagram support (via extensions)

### 8. Admin Panel Improvements
- Drag-and-drop document reordering
- Bulk operations (import/export via drag and drop)
- Version history for documents (conceptual)
- User management (extensible for multi-user support)

### 9. Performance Features
- Lazy loading for images
- Prefetching of next documents
- Offline support (PWA-ready structure)

### 10. Accessibility
- Better ARIA labels for screen readers
- Keyboard shortcuts documentation
- Screen reader improvements
- Focus management for keyboard navigation

## Search Functionality

The application now includes powerful search capabilities:

1. **Global Search**: Search across all courses and documents from the homepage, courses page, or any document page
2. **Contextual Results**: Search results show the document name, course, and content excerpt
3. **Real-time Search**: Results update as you type with debouncing to prevent excessive requests
4. **Direct Navigation**: Click on search results to go directly to the relevant document
5. **Keyboard Navigation**: Use arrow keys and Enter to navigate search results

## Mobile Experience

The mobile experience has been completely revamped:

1. **Responsive Design**: Adapts to all screen sizes
2. **Mobile TOC**: Dedicated table of contents button for mobile devices
3. **Touch Optimized**: Larger touch targets for better mobile interaction
4. **Performance**: Optimized loading and rendering for mobile devices

## Admin Panel Features

The admin panel includes advanced functionality:

1. **Course Management**: Create, edit, delete, and reorder courses
2. **Document Management**: Create, edit, and delete documents within courses
3. **Bulk Operations**: Import multiple documents via drag and drop
4. **Visual Feedback**: Toast notifications for all actions
5. **Responsive Design**: Works on all device sizes