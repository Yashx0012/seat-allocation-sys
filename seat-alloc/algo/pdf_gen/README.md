# PDF Generation Module

The `pdf_gen/` directory handles the transformation of seating data into formatted, printable PDF documents and attendance sheets.

## Key Components

- **[pdf_generation.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/pdf_gen/pdf_generation.py)**: The main engine for creating PDF files. It handles coordinate math, font styling, and the layout of seating grids.
- **[template_manager.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/pdf_gen/template_manager.py)**: Manages dynamic PDF templates, allowing for customizable headers, footers, and logos.
- **[database.py](file:///home/blazex/Documents/git/seat-allocation-sys/algo/pdf_gen/database.py)**: Manages the local `pdf_templates.db`, which stores template configurations separate from the main allocation data.

## Process Flow

1. **Data Retrieval**: Seating data is retrieved either from the **Manual Cache** (active sessions) or the **Relational Database** (finalized sessions).
2. **Layout Calculation**: The generator calculates the dimensions for each seat "cell" based on the classroom configuration (rows/cols).
3. **Rendering**: Uses standard PDF libraries to draw the grid, fill colors (based on batch), and overlay student names/enrollments.
4. **Storage**: Generated PDFs are temporarily stored in `seat_plan_generated/` before being served to the user or compressed into an export archive.

## Special Features
- **Vectorized Layouts**: High-resolution output suitable for large-format prints.
- **Attendance Sheets**: Automatically generated alongside seating plans, featuring student names and signature slots.
- **Bulk Export**: Supports zipping multiple room plans into a single archive for complete session reporting.
