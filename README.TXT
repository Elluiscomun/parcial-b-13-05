# Proyecto: Gestión de Reservas de Citas Médicas

## Descripción
Este proyecto implementa un sistema de gestión de reservas de citas médicas para una clínica en línea. Los pacientes pueden crear reservas y consultar su estado. Las reservas se procesan de manera asíncrona utilizando RabbitMQ, lo que permite manejar las solicitudes en una cola y actualizar su estado a "agendado".

## Tecnologías Utilizadas
- **FastAPI**: Framework para la creación de la API REST.
- **SQLite**: Base de datos ligera para almacenar las reservas.
- **RabbitMQ**: Sistema de mensajería para manejar las reservas en una cola.
- **Docker**: Contenedores para la aplicación y sus servicios.
- **Docker Compose**: Orquestación de los servicios.

## Funcionalidades
1. **Crear Reserva**:
   - Endpoint: `POST /book/`
   - Permite a los pacientes crear una nueva reserva con su nombre.
   - La reserva se agrega a una cola en RabbitMQ para ser procesada.

2. **Consultar Estado de Reserva**:
   - Endpoint: `GET /book/{id}`
   - Permite consultar el estado de una reserva específica (`pending`, `agendado`).

3. **Procesamiento Asíncrono**:
   - Las reservas se procesan desde la cola RabbitMQ cada 10 segundos.
   - El estado de la reserva se actualiza a `agendado` después de ser procesada.

## Configuración y Ejecución

### Requisitos Previos
- Docker y Docker Compose instalados en el sistema.

### Pasos para Ejecutar
1. **Clonar el proyecto**:
   Asegúrate de que todos los archivos del proyecto estén en el directorio correcto.

2. **Construir y ejecutar los contenedores**:
   Ejecuta los siguientes comandos en la terminal:
   ```bash
   docker-compose down
   docker-compose up --build