# Agente Scaffold Quarkus PMR — Guida per i colleghi

Questo repository include un agente AI specializzato nella generazione di
microservizi Quarkus seguendo i pattern del progetto PMR.

---

## Prerequisiti

| Strumento | Versione minima | Verifica |
|---|---|---|
| Git | qualsiasi | `git --version` |
| GitHub CLI | 2.x | `gh --version` |
| GitHub Copilot CLI extension | qualsiasi | `gh extension list` |
| Python | 3.8+ | `python3 --version` |
| Java | 21 | `java -version` |
| Maven | 3.9+ | `mvn -v` |

### Installare GitHub Copilot CLI (se non lo hai)

```bash
gh extension install github/gh-copilot
```

Verifica che funzioni:

```bash
gh copilot --version
```

---

## Passo 1 — Clona il repository

```bash
git clone <url-del-repository>
cd <nome-repository>
```

---

## Passo 2 — Posizionati nella cartella `java`

**Importante:** l'agente funziona **solo se sei nella cartella `java`** (o in una
sua sottocartella). Il file `.github/copilot-instructions.md` viene caricato
automaticamente da Copilot CLI quando si trova nella directory corrente o in
una parent.

```bash
cd java
```

Verifica di essere nel posto giusto:

```bash
ls scaffold_quarkus.py   # deve esistere
ls .github/copilot-instructions.md   # deve esistere
```

---

## Passo 3 — Avvia Copilot CLI

```bash
gh copilot chat
```

> Si apre una sessione di chat interattiva. L'agente riconosce automaticamente
> il contesto PMR grazie al file `.github/copilot-instructions.md`.

---

## Passo 4 — Chiedi lo scaffold

Scrivi in linguaggio naturale quello che vuoi generare. Esempi:

**Microservizio Frontiera** (REST proxy, senza DB):
```
Genera uno scaffold Frontiera chiamato "gestione-contratti"
con package "it.eng.snam.pmr.gestionecontratti"
```

**Microservizio DataGateway** (con DB, scheduler, Kafka consumer attivo):
```
Genera uno scaffold DataGateway chiamato "gestione-contratti-dg"
con package "it.eng.snam.pmr.gestionecontrattidg"
```

**Microservizio + libreria comune custom** (tutto da zero, nessuna dipendenza):
```
Genera uno scaffold Frontiera chiamato "gestione-contratti"
con package "it.eng.snam.pmr.gestionecontratti"
e una libreria custom chiamata "mia-common-lib"
con package "it.eng.snam.pmr.common"
```

**Solo la libreria comune**:
```
Genera solo la libreria comune chiamata "mia-common-lib"
con package "it.eng.snam.pmr.common"
```

L'agente farà le domande necessarie e lancerà il comando corretto.

---

## Passo 5 — Installa ed avvia

### Se hai generato anche la libreria

```bash
# 1. Installa la libreria nel tuo repo Maven locale
cd <nome-libreria>
mvn install

# 2. Torna nella cartella del microservizio e avvialo
cd ../<nome-microservizio>
mvn quarkus:dev
```

### Se usi la pmr-common-library già pubblicata su Nexus

```bash
cd <nome-microservizio>
mvn quarkus:dev
```

---

## Struttura generata

### Frontiera (~27 file)

```
<nome-servizio>/
├── pom.xml
├── Dockerfile.hybrid-devops
├── src/main/resources/application.properties
├── src/test/resources/application-test.properties
└── src/main/java/<package>/
    ├── config/         ApplicationConfig, OpenApiConfig
    ├── filter/         MdcHeadersFilter, GlobalHeadersOpenApiFilter
    ├── health/         ApplicationHealthCheck
    ├── kafka/          KafkaGenericProducer, KafkaGenericConsumer
    ├── service/        TopicService, SampleService
    ├── resource/       SampleResource
    ├── client/         SampleDgClient          ← chiama il DataGateway
    ├── dto/            SampleDTO
    ├── exception/      RemoteCallException, RetryableRemoteException
    ├── response/       GenericResponse, ResponseStatus
    └── utils/          Constants, RequestCtx, Utility, JsonUtils, MessageTypeEnum
```

### DataGateway (~33 file, aggiunge rispetto al Frontiera)

```
<nome-servizio-dg>/
├── src/main/resources/db/migration/V1__CREATE_TABLES.sql
└── src/main/java/<package>/
    ├── domain/         <Entità>Entity, RevisionInfo    ← JPA + Envers
    ├── repository/     <Entità>Repository              ← PanacheRepository
    ├── mapper/         <Entità>Mapper                  ← MapStruct
    └── scheduler/      ScheduledJob, ShedLockConfig    ← cron + ShedLock
```

---

## Tipi di microservizio a confronto

| Caratteristica | Frontiera | DataGateway (`-dg`) |
|---|---|---|
| Accesso DB | ❌ | ✅ MSSQL + JPA Panache |
| Migrazioni DB | ❌ | ✅ Flyway |
| Audit storico | ❌ | ✅ Hibernate Envers |
| Scheduler | ❌ | ✅ Quarkus Scheduler + ShedLock |
| Kafka consumer | opzionale | ✅ attivo |
| Kafka producer | ✅ | ✅ |
| Redis / Cache | ✅ | ✅ |
| Client REST verso DG | ✅ | ❌ (è lui il DG) |
| Autorizzazione (`@AuthzRead`) | ✅ | ❌ (delegata al Frontiera) |

---

## Comandi diretti (senza chat)

Se preferisci lanciare lo script direttamente senza usare la chat:

```bash
# Frontiera
python3 ./scaffold_quarkus.py \
  --type frontiera \
  --service-name  <nome-servizio> \
  --base-package  <package.java> \
  --output-dir    .

# DataGateway
python3 ./scaffold_quarkus.py \
  --type datagateway \
  --service-name  <nome-servizio-dg> \
  --base-package  <package.java> \
  --output-dir    .

# Frontiera + libreria custom
python3 ./scaffold_quarkus.py \
  --type         frontiera \
  --service-name <nome-servizio> \
  --base-package <package.java> \
  --lib-name     <nome-libreria> \
  --lib-package  <package.libreria> \
  --output-dir   .

# Solo libreria
python3 ./scaffold_quarkus.py \
  --lib-only \
  --lib-name    <nome-libreria> \
  --lib-package <package.libreria> \
  --output-dir  .

# Aiuto completo
python3 ./scaffold_quarkus.py --help
```

---

## Dopo la generazione — cosa fare

1. **Rinomina** le classi `Sample*` con i nomi reali delle tue entità di dominio
2. **Configura** i topic Kafka in `Constants.java` → interfaccia `Topic`
3. **Configura** `application.properties` con i valori reali (DB, Kafka, OIDC)
4. *(solo DG)* Aggiorna la migrazione `V1__CREATE_TABLES.sql` con le tue tabelle reali
5. *(solo DG)* Imposta le variabili d'ambiente: `DB_URL`, `DB_USERNAME`, `DB_PASSWORD`
