# Визуализации (текущее состояние)

Набор диаграмм с разных точек зрения. Только текущее состояние проекта.

## 1) Контекст системы
```mermaid
%%{init: {"theme":"base","themeVariables": {"background":"#000000","primaryTextColor":"#FFFFFF","lineColor":"#FFFFFF","secondaryColor":"#0d1117","tertiaryColor":"#161b22","primaryColor":"#0d1117"}}}%%
flowchart LR
  User((Пользователь)) -->|чаты| TG[Telegram]
  TG -->|Polling| App[Приложение бота]
  App -->|chat.completions| OR[(OpenRouter API)]
```

## 2) Компоненты приложения
```mermaid
%%{init: {"theme":"base","themeVariables": {"background":"#000000","primaryTextColor":"#FFFFFF","lineColor":"#FFFFFF","secondaryColor":"#0d1117","tertiaryColor":"#161b22","primaryColor":"#0d1117"}}}%%
flowchart LR
  subgraph App[Приложение]
    C[Config]
    R[RoleManager]
    CM[ConversationManager]
    L[LLMClient]
    H[MessageHandler]
    B[TelegramBot]
  end
  C --> R
  C --> L
  R --> H
  CM --> H
  L --> H
  H --> B
  B -. polling .->|aiogram| TG[Telegram]
```

## 3) Последовательность обработки текстового сообщения
```mermaid
%%{init: {"theme":"base","themeVariables": {"background":"#000000","primaryTextColor":"#FFFFFF","lineColor":"#FFFFFF","secondaryColor":"#0d1117","tertiaryColor":"#161b22","primaryColor":"#0d1117"}}}%%
sequenceDiagram
  participant T as Telegram
  participant B as TelegramBot/Dispatcher
  participant H as MessageHandler
  participant CM as ConversationManager
  participant R as RoleManager
  participant L as LLMClient

  T->>B: Текст
  B->>H: Делегирование обработчику
  H->>CM: get_history(user_id)
  H->>R: load_role()
  H->>L: chat.completions(system+history+user)
  L-->>H: Ответ ассистента
  H->>CM: add_message(user, assistant, content)
  H-->>T: Ответ пользователю
```

## 4) Поток данных
```mermaid
%%{init: {"theme":"base","themeVariables": {"background":"#000000","primaryTextColor":"#FFFFFF","lineColor":"#FFFFFF","secondaryColor":"#0d1117","tertiaryColor":"#161b22","primaryColor":"#0d1117"}}}%%
flowchart TB
  U[Текст пользователя] --> H[MessageHandler]
  R[RoleManager: роль из файла] --> H
  H -->|формирует| M[[messages: system + history + user]]
  CM[ConversationManager: in-memory] --> H
  H --> L[LLMClient]
  L --> OR[(OpenRouter API)]
  OR --> L
  L --> H
  H -->|обновляет| CM
  H --> A[Ответ пользователю]
```

## 5) Состояние диалога (упрощённо)
```mermaid
%%{init: {"theme":"base","themeVariables": {"background":"#000000","primaryTextColor":"#FFFFFF","lineColor":"#FFFFFF","secondaryColor":"#0d1117","tertiaryColor":"#161b22","primaryColor":"#0d1117"}}}%%
stateDiagram-v2
  [*] --> Empty
  Empty: История отсутствует
  Empty --> HasHistory: add_message(user)
  HasHistory --> HasHistory: add_message(user|assistant)
  HasHistory --> Empty: clear_history
```

## 6) Развёртывание (упрощённо)
```mermaid
%%{init: {"theme":"base","themeVariables": {"background":"#000000","primaryTextColor":"#FFFFFF","lineColor":"#FFFFFF","secondaryColor":"#0d1117","tertiaryColor":"#161b22","primaryColor":"#0d1117"}}}%%
flowchart LR
  subgraph Local[Локальная машина / среда выполнения]
    Proc[Процесс Python\nuv + aiogram polling]
  end
  TG[Telegram] -. long polling .- Proc
  Proc --> OR[(OpenRouter API)]
```

## 7) Модель данных (логическая, in-memory)
```mermaid
%%{init: {"theme":"base","themeVariables": {"background":"#000000","primaryTextColor":"#FFFFFF","lineColor":"#FFFFFF","secondaryColor":"#0d1117","tertiaryColor":"#161b22","primaryColor":"#0d1117"}}}%%
erDiagram
  USER ||--o{ MESSAGE : has
  CONVERSATION ||--o{ MESSAGE : contains
  USER ||--o{ CONVERSATION : per_user

  USER {
    int id
  }
  CONVERSATION {
    int user_id
    // хранится в памяти процесса
  }
  MESSAGE {
    string role
    string content
  }
```

## 8) Пакеты/файлы (высокоуровнево)
```mermaid
%%{init: {"theme":"base","themeVariables": {"background":"#000000","primaryTextColor":"#FFFFFF","lineColor":"#FFFFFF","secondaryColor":"#0d1117","tertiaryColor":"#161b22","primaryColor":"#0d1117"}}}%%
flowchart TB
  subgraph src/bot
    cfg[config.py]
    conv[conversation.py]
    role[role_manager.py]
    llm[llm_client.py]
    h[handlers.py]
    b[bot.py]
    m[__main__.py]
  end
  subgraph tests
    t[unit + integration]
  end
  subgraph docs
    d[ADR / README / guides]
  end
  subgraph prompts
    p[role.txt]
  end

  cfg --> role
  cfg --> llm
  conv --> h
  role --> h
  llm --> h
  h --> b
  m --> b
```

