# 🌐 NewsGPT Navigator — Frontend

This is the React-based web interface for the NewsGPT Navigator platform. It provides a real-time, interactive dashboard for exploring news intelligence across the 10-agent pipeline.

---

## 🚀 Features

- **Interactive Dashboard**: Real-time visualization of the 10-stage execution pipeline.
- **Multimodal Output**: Integrated audio player and related YouTube video section.
- **Entity & Trend Analysis**: Visualizes entity sentiment and long-form story arcs.
- **Persona Comparison**: View how different personas (CFO, Student, Investigator) perceive the same news.
- **Conflict Tracking**: Highlights factual and narrative contradictions surfaced by the agents.
- **Multilingual Support**: Switch seamlessly between 8 languages for the entire briefing output.

---

## 🛠️ Tech Stack

- **Framework**: React 19 (TypeScript)
- **Bundler**: Vite 8
- **Styling**: Tailwind CSS 4
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **API Client**: Standard `fetch` with Zod/TypeScript interface safety

---

## ⚡ Development

```bash
# Install dependencies
npm install

# Start development server (with backend proxy)
npm run dev
```

The app will be available at `http://localhost:5173`.

> [!NOTE]
> The development server is configured to proxy API requests (`/analyze`, `/health`, etc.) to the FastAPI backend at `http://127.0.0.1:8000`.

---

## 🏗️ Production Build

To build the project for production:

```bash
npm run build
```

The output will be generated in the `dist/` directory, which is automatically served by the FastAPI backend when placed in the correct location.

---

## 📁 Structure

- `src/api`: API client and endpoint definitions.
- `src/components`: Reusable UI components (Glass cards, buttons, skeletons).
- `src/views`: Main application views (Dashboard, Timeline, Videos, etc.).
- `src/types`: TypeScript interfaces for the API briefing payload.
- `src/config`: Pipeline and application configuration.
