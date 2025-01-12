# 🏘️ Degent Civil

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![Documentation](https://img.shields.io/badge/docs-online-blue.svg)](https://KingJiongEN.github.io/DegentCivil/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

*A sophisticated AI-driven town simulation system with autonomous characters, dynamic interactions, and realistic behaviors.*

[📚 Documentation](https://KingJiongEN.github.io/DegentCivil/) | [🚀 Quick Start](https://KingJiongEN.github.io/DegentCivil/latest/getting-started/installation/) | [💡 Examples](https://KingJiongEN.github.io/DegentCivil/latest/examples/add_new_state) | [🤝 Contributing](https://KingJiongEN.github.io/DegentCivil/latest/developer-guide/contributing/)

</div>

## ✨ Features

- **🤖 AI-Driven Characters**: Autonomous NPCs with realistic behaviors and decision-making capabilities
- **🔄 Dynamic State Management**: Sophisticated state system for character behaviors and interactions
- **⚡ Real-time Simulation**: Live updates and interactions within the town environment
- **🧠 Memory System**: Advanced memory management using vector embeddings and semantic search
- **🏢 Building System**: Flexible building management with dynamic interactions
- **🔗 LLM Integration**: Seamless integration with Large Language Models for natural interactions

## 📋 Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- OpenAI API access (or compatible LLM service)

## 🚀 Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/KingJiongEN/DegentCivil.git
cd DegentCivil
```

2. **Set Up Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Start Required Services**
```bash
# Start Milvus
mkdir -p milvus/{db,minio}
docker-compose -f docker-compose_milvus.yml up -d

# Start Redis
docker run --name my-redis -p 6379:6379 -d redis
```

4. **Run the Service**
```bash
DEBUG=1 Milvus=1 python main.py
```

## 📚 Documentation

Visit our comprehensive documentation for detailed information:

- [🏁 Getting Started Guide](https://KingJiongEN.github.io/DegentCivil/getting-started/installation)
- [📖 Core Concepts](https://KingJiongEN.github.io/DegentCivil/core-concepts/overview)
  - [Character System](https://KingJiongEN.github.io/DegentCivil/core-concepts/character-system)
  - [State Management](https://KingJiongEN.github.io/DegentCivil/core-concepts/state-management)
  - [Memory System](https://KingJiongEN.github.io/DegentCivil/core-concepts/memory-system)
  - [Building System](https://KingJiongEN.github.io/DegentCivil/core-concepts/building-system)
  - [Simulation Logic](https://KingJiongEN.github.io/DegentCivil/core-concepts/simulation-logic)
- [🔧 API Reference](https://KingJiongEN.github.io/DegentCivil/api-reference/models/town)
- [📈 Advanced Topics](https://KingJiongEN.github.io/DegentCivil/advanced-topics/custom-states)
- [💻 Developer Guide](https://KingJiongEN.github.io/DegentCivil/developer-guide/contributing)

## 🛠️ Development Tools

### Milvus Visualization
- URL: `localhost:18000`
- Username: `minioadmin`
- Password: `minioadmin`

### Memory Demo
```bash
export PYTHONPATH="{project_path}:$PYTHONPATH"
export OPENAI_API_KEY=your_api_key_here
python -m app.models.memory
```

## 📁 Project Structure

```
DegentCivil/
├── app/                    # Main application directory
│   ├── main.py            # Application entry point
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── llm/               # LLM integration
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── docs/                  # Documentation
└── tests/                 # Test suite
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://KingJiongEN.github.io/DegentCivil/developer-guide/contributing) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- OpenAI for LLM capabilities
- Milvus for vector database
- Redis for caching
- All our contributors

---
<div align="center">
Made with ❤️ by the Town Simulation Team
</div>

