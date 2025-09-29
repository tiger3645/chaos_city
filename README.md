# Ciudad del Caos

Un juego de cartas estratégico para 2 jugadores ambientado en Chicago, 1946. Los jugadores luchan por el control de la ciudad utilizando diferentes facciones: Policías, Mafiosos, Detectives, Ladrones y Wildcards.

## Estructura del Proyecto

```
chaos_city/
├── backend/           # Servidor Python con WebSocket
│   ├── models.py      # Modelos de datos del juego
│   ├── game_engine.py # Lógica principal del juego
│   ├── server.py      # Servidor WebSocket
│   ├── run_server.py  # Script de inicio del servidor
│   └── requirements.txt
├── frontend/          # Cliente React con Vite
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── ...
│   ├── package.json
│   └── ...
├── BASE_IDEA.md      # Reglas completas del juego
└── CARDS.md          # Cartas iniciales de cada facción
```

## Instalación y Configuración

### Backend (Python)

1. Navegar a la carpeta backend:
```bash
cd backend
```

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar el servidor:
```bash
python run_server.py
```

El servidor estará disponible en `ws://localhost:8000`

### Frontend (React + Vite)

1. Navegar a la carpeta frontend:
```bash
cd frontend
```

2. Instalar dependencias:
```bash
npm install
```

3. Ejecutar el servidor de desarrollo:
```bash
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

## Cómo Jugar

1. **Conexión**: Abrir el frontend en el navegador
2. **Crear Juego**: 
   - Seleccionar "Crear Juego"
   - Configurar nombres y facciones de ambos jugadores
   - Hacer clic en "Crear Juego"
3. **Alternativamente, Unirse**: Si ya existe un juego, usar su ID para unirse
4. **Gameplay**: 
   - Cada turno tiene 4 fases: Robo, Despliegue, Acciones, Resolución
   - Jugar cartas en las zonas correspondientes (Brutos, Tiradores, Charlatanes)
   - Atacar con personajes para reducir la reputación del oponente
   - ¡El primero en reducir la reputación enemiga a 0 gana!

## Características Técnicas

### Backend
- **WebSocket**: Comunicación en tiempo real entre jugadores
- **FastAPI**: Framework web moderno para Python
- **Arquitectura Modular**: Separación clara entre modelos, lógica de juego y servidor
- **Gestión de Estado**: Estado completo del juego sincronizado entre clientes

### Frontend
- **React 18**: Biblioteca de UI moderna
- **TypeScript**: Tipado estático para mayor robustez
- **Vite**: Build tool rápido y moderno
- **Tailwind CSS**: Framework de utilidades CSS
- **Lucide React**: Iconos modernos
- **WebSocket Hook**: Hook personalizado para manejo de conexiones en tiempo real

## Facciones del Juego

### 👮 Policías
- **Identidad**: Control y resistencia
- **Fortaleza**: vs Ladrones
- **Debilidad**: vs Mafiosos
- **Líder**: Capitán O'Reilly

### 🔫 Mafiosos  
- **Identidad**: Agresión y fuerza bruta
- **Fortaleza**: vs Policías
- **Debilidad**: vs Detectives
- **Líder**: Don Moretti

### 🔍 Detectives
- **Identidad**: Astucia e investigación
- **Fortaleza**: vs Mafiosos
- **Debilidad**: vs Ladrones
- **Líder**: Detective Sullivan

### 🎭 Ladrones
- **Identidad**: Sigilo y evasión
- **Fortaleza**: vs Detectives
- **Debilidad**: vs Policías
- **Líder**: "La Sombra"

### ⭐ Wildcards
- **Identidad**: Caos y flexibilidad
- **Sin ventajas/debilidades fijas**
- **Líder**: El Tahúr

## Desarrollo

### Comandos Útiles

**Backend**:
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python run_server.py

# Ejecutar con auto-reload (desarrollo)
uvicorn server:app --reload --host localhost --port 8000
```

**Frontend**:
```bash
# Instalar dependencias
npm install

# Servidor de desarrollo
npm run dev

# Build de producción
npm run build

# Preview del build
npm run preview

# Linting
npm run lint
```

## Próximas Características

- [ ] Sistema de autenticación
- [ ] Salas de juego públicas/privadas
- [ ] Espectadores
- [ ] Replay de partidas
- [ ] Estadísticas de jugadores
- [ ] Mazos personalizables
- [ ] Torneos
- [ ] Chat en juego
- [ ] Efectos visuales mejorados
- [ ] Sonidos y música

## Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Créditos

Inspirado en los juegos de cartas clásicos y la atmósfera noir de Chicago en los años 40.