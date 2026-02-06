# GUÍA DE USO Y ADAPTACIÓN DEL PROTOCOLO MAESTRO

El `PROTOCOLO_MAESTRO_IA_SEGURO.md` está diseñado para ser modular. Los **Principios de Seguridad (Zero Trust, Tipado Estricto)** son innegociables, pero las **Herramientas (Database, Auth)** son intercambiables.

Aquí tienes cómo instruir a un Agente IA para iniciar un proyecto usando el protocolo pero cambiando la tecnología base.

---

## 💡 EJEMPLO 1: Cambiar Supabase por FIREBASE

Si prefieres Firebase, mantienes la arquitectura "Feature-First" y la seguridad, pero cambias RLS por "Firestore Rules".

### 👉 Prompt para copiar al Agente:

```text
Actúa como mi Arquitecto de Software Principal.
Vamos a iniciar un nuevo proyecto llamado "TaskMaster".

Quiero que apliques estrictamente el 'PROTOCOLO_MAESTRO_IA_SEGURO.md' que te adjunto (o que está en mi contexto), con una EXCEPCIÓN en el Stack Tecnológico:

1. MODIFICACIÓN DEL STACK:
   - Base de Datos: Usaremos **Firebase Firestore** en lugar de Supabase.
   - Auth: **Firebase Auth**.
   - Backend: Next.js Server Actions (igual que el protocolo).

2. ADAPTACIÓN DE SEGURIDAD (CRÍTICO):
   - En lugar de "Supabase RLS", quiero que generes un archivo `firestore.rules` robusto al principio.
   - Aplica el principio "Zero Trust": Por defecto `allow read, write: if false;` y abre permisos solo por colección.
   - Mantén el uso de **Zod** para validar todos los inputs en las Server Actions antes de escribir en Firestore.

3. ESTRUCTURA:
   - Mantén la arquitectura "Feature-First" (src/features/...).
   - En `src/shared/database`, inicializa la conexión de Firebase Admin.

Empieza creando la estructura de carpetas y la configuración de Firebase siguiendo estos principios.
```

---

## 💡 EJEMPLO 2: Cambiar Supabase por PRISMA + POSTGRES (Self-Hosted)

Si quieres usar un Postgres estándar (ej: en Docker o AWS RDS) con Prisma ORM.

### 👉 Prompt para copiar al Agente:

```text
Actúa como mi Arquitecto. Nuevo proyecto: "InventoryPro".

Aplica el 'PROTOCOLO_MAESTRO_IA_SEGURO.md' con el siguiente cambio de infraestructura:

1. SWAP DE TECNOLOGÍA:
   - Elimina Supabase.
   - Usa **Prisma ORM** con una base de datos PostgreSQL estándar.
   - Usa **NextAuth.js (Auth.js)** para la autenticación.

2. ADAPTACIÓN DE SEGURIDAD:
   - Como no tenemos RLS de base de datos, la seguridad debe estar en la capa de aplicación (Service Layer).
   - REGLA: Cada Server Action debe verificar `session.user` ANTES de hacer cualquier consulta a Prisma.
   - Validación: Zod sigue siendo MANDATORIO para validar inputs.

3. FLUJO DE TRABAJO:
   - Fase 1: Define el `schema.prisma` primero.
   - Fase 2: Genera los tipos con `npx prisma generate`.
   - Fase 3: Crea los servicios en `src/features/[feature]/services/`.

Inicia el proyecto configurando Prisma y NextAuth.
```

---

## 🛡️ LO QUE NUNCA CAMBIA (INVARIANTES)

Aunque cambies la base de datos, **esto se mantiene para garantizar calidad**:

1.  **Strict TypeScript**: Nunca permitas `any`.
2.  **Feature-First**: No tires todo en `components/` desordenados. Organiza por `features/auth`, `features/billing`.
3.  **Zod Everywhere**:
    *   Con Supabase: `Zod -> Server Action -> Supabase`
    *   Con Firebase: `Zod -> Server Action -> Firestore`
    *   Con Prisma: `Zod -> Server Action -> Prisma`
    *   *La validación de entrada es la primera línea de defensa, sin importar la DB.*
4.  **Auditoría**: El agente debe seguir confirmando sus planes antes de escribir código masivo.

---

## 🚀 RESUMEN

Para usar el protocolo con otras herramientas, solo usa esta fórmula en tu prompt:

> "Sigue el PROTOCOLO MAESTRO, pero reemplaza **[Tecnología del Protocolo]** por **[Tu Tecnología Preferida]**. Asegúrate de que los principios de **[Seguridad/Validación/Orden]** se adapten a esta nueva herramienta."
