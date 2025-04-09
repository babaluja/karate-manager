#!/usr/bin/env python3
import re

routes_to_protect = [
    "@app.route('/athletes/<int:athlete_id>/edit', methods=['GET', 'POST'])",
    "@app.route('/athletes/<int:athlete_id>/delete', methods=['POST'])",
    "@app.route('/payments', methods=['GET'])",
    "@app.route('/athletes/<int:athlete_id>/payments/add', methods=['POST'])",
    "@app.route('/payments/<int:payment_id>/delete', methods=['POST'])",
    "@app.route('/athletes/<int:athlete_id>/exams/add', methods=['POST'])",
    "@app.route('/exams/<int:exam_id>/delete', methods=['POST'])",
    "@app.route('/reports')",
    "@app.route('/api/athletes/search')",
    "@app.route('/api/monthly-data')",
    "@app.route('/api/belt-distribution')"
]

with open('routes.py', 'r') as f:
    content = f.read()

for route in routes_to_protect:
    pattern = f"{route}\\ndef "
    replacement = f"{route}\n@login_required\ndef "
    content = re.sub(pattern, replacement, content)

with open('routes.py', 'w') as f:
    f.write(content)

print("Routes protected with login_required")
