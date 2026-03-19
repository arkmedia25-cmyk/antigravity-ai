---
name: trainer
description: Use when the user provides new knowledge, training data, audience info, product info, or wants to teach the system.
---

# Trainer

## 🎯 Purpose
Store and structure new knowledge provided by the user so it can be used in future responses.

---

## 🧠 When to Use
- When user shares audience insights
- When user gives product details
- When user provides marketing knowledge
- When user uses "/train" command
- When user wants system to remember something

---

## 📥 Inputs
- category (audience, hooks, products, funnels, etc.)
- content (text to store)

---

## ⚙️ Steps
1. Identify category of information
2. Clean and structure content
3. Save to memory system
4. Confirm storage

---

## 📤 Output Format

### 🔹 Summary
- What was saved
- Category

### 🔹 Details
- Structured version of saved content

---

## 🚫 Avoid
- Storing unclear or useless data
- Overwriting important information
- Ignoring category structure

---

## 💡 Notes
- Treat all user knowledge as valuable
- Improve system intelligence over time
- Support long-term learning