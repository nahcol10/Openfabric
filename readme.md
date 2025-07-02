# 🚀 Openfabric AI Developer Challenge – Creative Partner

Welcome to **Creative Partner**, an intelligent AI pipeline that brings your imagination to life. This system provides a complete text-to-3D generation pipeline with advanced memory management and session handling.

## ✨ What This System Does

✅ **Prompt Enhancement**: Uses local LLM (`llama3.2`) to optimize user prompts for better 3D generation  
✅ **Image Generation**: Converts enhanced text to high-quality images via Openfabric Text-to-Image app  
✅ **3D Model Creation**: Transforms images into detailed 3D models (.glb format) with preview videos  
✅ **Smart Memory**: Maintains both short-term (Redis) and long-term (FAISS) conversation memory  
✅ **Session Management**: User-specific sessions with 30-minute timeout and activity tracking  
✅ **Multiple Interfaces**: REST API + Interactive Gradio UI  

---

## 🏗️ System Architecture

```
User Input (REST API / Gradio UI)
 ↓
Session Manager
 ├── Creates user-specific sessions (username_sessionid)
 ├── 30-minute timeout with activity tracking
 └── Memory integration per session
 ↓
Memory Manager
 ├── Short-term: Redis chat history (30min TTL)
 ├── Long-term: FAISS vector embeddings
 └── Context retrieval for conversational AI
 ↓
LLM Prompt Enhancement
 ├── Model: llama3.2 via Ollama
 ├── System prompt optimized for 3D generation
 └── 60-word limit for enhanced prompts
 ↓
Text-to-Image Generation
 ├── App: c25dcd829d134ea98f5ae4dd311d13bc.node3.openfabric.network
 ├── Input: Enhanced text prompt
 └── Output: High-quality image (PNG)
 ↓
Image-to-3D Conversion
 ├── App: 5891a64fe34041d98b0262bb1175ff07.node3.openfabric.network
 ├── Input: Base64-encoded image
 └── Output: 3D model (.glb) + Preview video (.mp4)
 ↓
File Management
 ├── Images: output_{session_id}.png
 ├── 3D Models: output_{session_id}.glb
 ├── Videos: preview_{session_id}.mp4
 └── Storage: app/output_3d_model/
```

---

## 📦 Technology Stack

| **Component** | **Technology** | **Purpose** |
|---------------|----------------|-------------|
| **Backend Framework** | Openfabric SDK 0.3.0 | Main application framework |
| **LLM** | llama3.2 (Ollama) | Prompt enhancement & conversation |
| **Short-term Memory** | Redis | Session-based chat history (30min TTL) |
| **Long-term Memory** | FAISS + SentenceTransformers | Vector embeddings for conversation recall |
| **Embeddings** | all-MiniLM-L6-v2 | Lightweight CPU-based text embeddings |
| **Text-to-Image** | Openfabric App | Professional image generation |
| **Image-to-3D** | Openfabric App | 3D model creation from images |
| **Session Management** | Custom Python | User session tracking & timeout |
| **UI Interface** | Gradio 4.x | Interactive web interface |
| **API Documentation** | Swagger UI | REST API documentation |
| **Container** | Docker | Deployment & isolation |
| **Date Parsing** | dateparser | Natural language date extraction |

---

## 🚀 Getting Started

### Prerequisites
- Docker installed
- Redis server running (for memory)
- Ollama with llama3.2 model (for LLM)

### Quick Start

1. **Start the main application:**
```bash
cd app/
python ignite.py
```
Access Swagger UI: `http://localhost:8888/swagger-ui`

2. **Launch Gradio interface:**
```bash
python chatbot_ui.py
```
Access UI: `http://localhost:7860`

3. **Using Docker:**
```bash
docker build -t creative-partner .
docker run -p 8888:8888 creative-partner
```

---

## 🎯 API Usage

### REST API Endpoint
**POST** `/execution`

**Request:**
```json
{
  "prompt": "A magical forest with glowing mushrooms",
  "username": "john_doe",
  "attachments": []
}
```

**Response:**
```json
{
  "message": "Successfully generated 3D model from prompt (Session: john_doe_a1b2c3d4)"
}
```

### Generated Files
- **Image**: `app/output_3d_model/output_john_doe_a1b2c3d4.png`
- **3D Model**: `app/output_3d_model/output_john_doe_a1b2c3d4.glb`
- **Preview Video**: `app/output_3d_model/preview_john_doe_a1b2c3d4.mp4`

---

## 🧠 Memory System

### Short-term Memory (Redis)
- **Storage**: Session-based chat history
- **TTL**: 30 minutes per session
- **Fallback**: In-memory storage if Redis unavailable
- **Format**: LangChain message history

### Long-term Memory (FAISS)
- **Storage**: Vector embeddings of conversations
- **Search**: Semantic similarity search
- **Metadata**: Date, session_id, user_id, type
- **Persistence**: In-memory with optional file save

### Memory Integration
```python
# Context retrieval example
context_msgs = session.memory.fetch_context(user_prompt)
# 1. Check recent Redis messages
# 2. Fallback to FAISS vector search
# 3. Return combined context for LLM
```

---

## 📁 Project Structure

```
app/
├── main.py                 # Main application logic
├── ignite.py              # Application startup
├── session_manager.py     # Session handling
├── chatbot_ui.py         # Gradio interface
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── start.sh              # Startup script
├── core/
│   ├── stub.py           # Openfabric app client
│   └── remote.py         # WebSocket proxy client
├── memory/
│   ├── __init__.py       # System prompts
│   ├── short_term_memory.py  # Redis integration
│   ├── long_term_memory.py   # FAISS vector store
│   └── memory_manager.py     # Memory coordination
├── ontology_*/           # Auto-generated schemas
├── config/               # Application configuration
├── datastore/            # Execution logs & state
└── output_3d_model/      # Generated files
```

---

## 🔧 Configuration

### App Configuration (`config/state.json`)
```json
{
  "super-user": {
    "app_ids": [
      "c25dcd829d134ea98f5ae4dd311d13bc.node3.openfabric.network",
      "5891a64fe34041d98b0262bb1175ff07.node3.openfabric.network"
    ]
  }
}
```

### Environment Variables
```bash
REDIS_URL=redis://localhost:6379/0
OLLAMA_URL=http://localhost:11434
```

---

## 📊 System Features

### Session Management
- **User-specific sessions**: `username_sessionid` format
- **Activity tracking**: Last activity timestamp
- **Timeout handling**: 30-minute automatic cleanup
- **Memory preservation**: Stores session summary before cleanup

### Error Handling
- **Redis fallback**: In-memory chat history when Redis unavailable
- **Connection resilience**: Handles Openfabric app failures gracefully
- **Logging**: Comprehensive error tracking in datastore/

### File Management
- **Session-based naming**: Prevents file conflicts
- **Multiple formats**: PNG images, GLB models, MP4 previews
- **Automatic cleanup**: Old files managed by session lifecycle

---

## 🎨 Example Outputs

**Input:** `"cat"`
**Session:** `lochan_8413bd70`
**Generated Files:**
- `output_lochan_8413bd70.png` - Enhanced cat image
- `output_lochan_8413bd70.glb` - 3D cat model

**Successful Response:**
```json
{"message": "Successfully generated 3D model from prompt (Session: lochan_8413bd70)"}
```

---

## 🔍 Monitoring & Debugging

### Execution Logs
- **Location**: `app/datastore/executions/`
- **Contains**: Input prompts, outputs, error traces
- **Format**: JSON with execution metadata

### Memory Logs
- **Short-term**: `app/datastore/short_term_log.jsonl`
- **Long-term**: In-memory FAISS store
- **Session tracking**: User activity and memory summary

---

## ⚡ Performance & Scalability

### Memory Efficiency
- **FAISS**: CPU-optimized vector operations
- **Redis TTL**: Automatic memory cleanup
- **Lightweight embeddings**: all-MiniLM-L6-v2 model

### Session Isolation
- **User separation**: Individual session namespaces
- **File organization**: Session-based file naming
- **Memory segmentation**: Per-user memory contexts

---

## 🛠️ Development & Customization

### Adding New Openfabric Apps
1. Update `config/state.json` with new app IDs
2. Modify `core/stub.py` for new app schemas
3. Update `main.py` execution pipeline

### Custom Memory Strategies
- **Short-term**: Modify `memory/short_term_memory.py`
- **Long-term**: Customize `memory/long_term_memory.py`
- **Integration**: Update `memory/memory_manager.py`

### Prompt Engineering
- **System prompt**: `memory/__init__.py`
- **Enhancement logic**: LLM chain in `short_term_memory.py`
- **Word limits**: 60-word optimization for 3D generation

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 🙏 Acknowledgments

- **[Openfabric AI](https://openfabric.network/)** - AI application platform
- **[Meta LLaMA](https://llama.meta.com/)** - Language model technology
- **[FAISS](https://github.com/facebookresearch/faiss)** - Vector similarity search
- **[LangChain](https://langchain.com/)** - LLM framework integration
- **[Gradio](https://gradio.app/)** - Interactive web interfaces

---

## 🎯 Future Enhancements

- [ ] Voice input integration
- [ ] Multiple 3D export formats
- [ ] Advanced prompt templates
- [ ] Batch processing capabilities
- [ ] Real-time collaboration features
- [ ] Custom model fine-tuning

---

**Creative Partner isn't just a tool—it's your AI-powered creative companion that remembers, learns, and grows with your imagination.** 🎨✨
