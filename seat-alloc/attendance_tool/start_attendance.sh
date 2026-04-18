#!/bin/bash
# Start attendance tool with proper cleanup

cd /home/harshitdv/Documents/seat-allocation-sys/seat-alloc/attendance_tool

echo "🚀 Starting Attendance Tool on port 5001..."
/home/harshitdv/Documents/seat-allocation-sys/.venv/bin/python run.py
