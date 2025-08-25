# Academic Documentation Portal

A Flask-based web application with an elegant, modern design for academic documentation and resources. This portal organizes content by courses, allowing students and educators to easily access markdown-based documents.

## Features

- Elegant modern design with focused document viewing
- Course-based organization of content
- Responsive design for all devices
- Markdown document support with syntax highlighting
- Powerful search functionality across all courses
- Clean, academic-focused interface
- Admin panel for content management

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd app
   ```

2. Install the required packages:
   ```bash
   pip install --break-system-packages -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to `http://localhost:80`

## Admin Panel

The portal includes an admin panel for managing courses and documents:

- **URL**: `http://localhost:80/admin`
- **Default Credentials**: 
  - Username: `admin`
  - Password: `password`

### Admin Features

1. **Dashboard**: Overview of courses and documents
2. **Course Management**: Create, edit, and view courses
3. **Document Management**: Create and edit markdown documents
4. **Live Preview**: View changes in the public portal

**Note**: For production use, you should change the default credentials in `app.py`.

## Course Structure

The portal organizes content by courses. Each course has its own directory with the following structure:

```
courses/
├── course_name/
│   ├── course.json
│   ├── docs/
│   │   ├── document1.md
│   │   ├── document2.md
│   │   └── ...
│   └── media/
│       ├── image1.png
│       ├── image2.jpg
│       └── ...
```

### Creating a New Course (Admin Panel)

1. Navigate to the admin panel
2. Go to "Courses" and click "New Course"
3. Fill in the course details
4. The system will automatically create the directory structure

### Adding Documents to a Course (Admin Panel)

1. Navigate to the admin panel
2. Go to "Courses" and select a course
3. Click "New Document"
4. Write your document using Markdown formatting

### Creating a New Course (Manual Method)

1. Create a new directory in the `courses/` folder with a descriptive name (use underscores for spaces)
2. Inside the course directory, create:
   - A `course.json` file with course metadata
   - A `docs/` directory for markdown documents
   - A `media/` directory for images and other media files

Example `course.json`:
```json
{
  "title": "Course Title",
  "description": "Brief description of the course",
  "instructor": "Instructor Name",
  "duration": "Course duration",
  "level": "Beginner/Intermediate/Advanced"
}
```

### Adding Documents to a Course (Manual Method)

1. Create markdown files (`.md` extension) in the `docs/` directory of a course
2. The document will automatically appear in the course page
3. Use standard markdown syntax for formatting

Example document structure:
```markdown
# Document Title

## Section 1
Content here...

## Section 2
More content...
```

### Adding Media to a Course

1. Place images and other media files in the `media/` directory of a course
2. Reference them in documents using relative paths:
   ```markdown
   ![Alt text](../media/image.png)
   ```

## Customization

### Theme
To customize the color scheme, modify the CSS variables in `static/css/style.css`:

```css
:root {
  --primary: #2563eb;      /* Primary color */
  --primary-dark: #1d4ed8; /* Darker variant */
  --primary-light: #3b82f6; /* Lighter variant */
  --secondary: #f1f5f9;    /* Background accent */
  --light: #ffffff;        /* Main background */
}
```

## License

This project is licensed under the MIT License.