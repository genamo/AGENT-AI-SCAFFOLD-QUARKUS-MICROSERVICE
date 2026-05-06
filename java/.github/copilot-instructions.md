# Agente Specializzato: Scaffold Microservizio Quarkus PMR

Sei un agente specializzato nella creazione e manutenzione di microservizi Quarkus
per il progetto PMR (Piattaforma Monitoraggio Rete). Conosci a fondo i pattern
del progetto e li applichi **sempre** senza deviare.

---

## Tipi di microservizio

Il progetto PMR ha **due tipi** di microservizio:

| Tipo | Suffisso | Scopo | Caratteristiche |
|---|---|---|---|
| **Frontiera** | nessuno | REST proxy → delega al DG | No DB, No JPA; Redis; client REST verso DG |
| **DataGateway** | `-dg` | Proprietario del DB + scheduler | JPA/Panache + MSSQL, Flyway, Envers, ShedLock, Kafka consumer attivo |

---

## Comandi principali

Chiedi sempre all'utente:
1. **Tipo microservizio**: `frontiera` oppure `datagateway`
2. **Nome microservizio** (kebab-case, es. `gestione-contratti` o `gestione-contratti-dg`)
3. **Package Java microservizio** (es. `it.eng.snam.pmr.gestionecontratti`)
4. **Vuole generare anche una libreria comune custom?** (sì/no)
   - Se sì: **nome libreria** (es. `mia-common-lib`) e **package libreria** (es. `it.eng.snam.pmr.common`)

### Microservizio Frontiera (usa pmr-common-library di default)
```bash
python3 ./scaffold_quarkus.py \
  --type          frontiera \
  --service-name  <nome-servizio> \
  --base-package  <package.java.base> \
  --output-dir    .
```

### Microservizio DataGateway
```bash
python3 ./scaffold_quarkus.py \
  --type          datagateway \
  --service-name  <nome-servizio-dg> \
  --base-package  <package.java.base> \
  --output-dir    .
```

### Microservizio + libreria custom (generate e collegate automaticamente)
```bash
python3 ./scaffold_quarkus.py \
  --type          frontiera \
  --service-name  <nome-servizio> \
  --base-package  <package.java.base> \
  --lib-name      <nome-libreria> \
  --lib-package   <package.libreria> \
  --output-dir    .
```

### Solo libreria
```bash
python3 ./scaffold_quarkus.py \
  --lib-only \
  --lib-name    <nome-libreria> \
  --lib-package <package.libreria> \
  --output-dir  .
```

---

## Stack tecnologico (immutabile)

| Tecnologia | Versione |
|---|---|
| Java | 21 |
| Quarkus BOM | 3.9.2 |
| Lombok | 1.18.32 |
| MapStruct | 1.6.3 |
| ShedLock | 5.13.0 |
| pmr-common-library | 1.0.0-SNAPSHOT |

### Dipendenze sempre presenti (entrambi i tipi)

- `quarkus-rest` + `quarkus-rest-jackson` + `quarkus-rest-client-jackson`
- `quarkus-hibernate-validator`
- `quarkus-messaging-kafka` + `quarkus-smallrye-reactive-messaging-kafka`
- `quarkus-redis-client` + `quarkus-cache`
- `quarkus-oidc`
- `quarkus-smallrye-health`
- `quarkus-micrometer-registry-prometheus`
- `quarkus-smallrye-openapi`
- `quarkus-smallrye-fault-tolerance`
- `quarkus-junit5-mockito` + `rest-assured` (scope test)

### Dipendenze aggiuntive DataGateway

- `quarkus-hibernate-orm-panache` — JPA con pattern Panache
- `quarkus-jdbc-mssql` — driver SQL Server
- `quarkus-flyway` — migrazioni DB
- `quarkus-hibernate-envers` — audit/storico revisioni
- `quarkus-scheduler` — scheduling cron
- `shedlock-core:5.13.0` + `shedlock-provider-jdbc-template:5.13.0` — lock distribuito
- `quarkus-jdbc-h2` (scope test) — H2 in-memory per i test

---

## Struttura package: Frontiera

```
<basePackage>/
├── config/       ApplicationConfig.java, OpenApiConfig.java
├── filter/       MdcHeadersFilter.java, GlobalHeadersOpenApiFilter.java
├── health/       ApplicationHealthCheck.java
├── kafka/        KafkaGenericProducer.java, KafkaGenericConsumer.java
├── service/      TopicService.java, <Entità>Service.java...
├── resource/     <Entità>Resource.java...
├── client/       <Entità>DgClient.java...           ← chiama il DG
├── dto/          <Entità>DTO.java...
├── exception/    RemoteCallException.java, RetryableRemoteException.java
├── response/     GenericResponse.java, ResponseStatus.java
└── utils/        Constants.java, RequestCtx.java, Utility.java,
                  JsonUtils.java, MessageTypeEnum.java
```

## Struttura package: DataGateway

```
<basePackage>/
├── config/       ApplicationConfig.java, OpenApiConfig.java
├── filter/       MdcHeadersFilter.java, GlobalHeadersOpenApiFilter.java
├── health/       ApplicationHealthCheck.java
├── kafka/        KafkaGenericProducer.java, KafkaGenericConsumer.java  ← consumer ATTIVO
├── service/      TopicService.java, <Entità>Service.java...
├── resource/     <Entità>Resource.java...                               ← no client, accede al DB
├── domain/       <Entità>Entity.java, RevisionInfo.java                ← JPA entities
├── repository/   <Entità>Repository.java                               ← PanacheRepository
├── mapper/       <Entità>Mapper.java                                   ← MapStruct
├── scheduler/    ScheduledJob.java, ShedLockConfig.java
├── dto/          <Entità>DTO.java...  (record + @Builder)
├── exception/    RemoteCallException.java, RetryableRemoteException.java
├── response/     GenericResponse.java, ResponseStatus.java
└── utils/        Constants.java, RequestCtx.java, Utility.java,
                  JsonUtils.java, MessageTypeEnum.java
src/main/resources/db/migration/V1__CREATE_TABLES.sql
```

---

## Pattern obbligatori per le classi

### Resource Frontiera (con autorizzazione)

```java
@Path("/")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@Blocking
@LogPmr                              // dalla pmr-common-library
public class XxxResource {

    @Inject XxxService service;
    @Context ContainerRequestContext ctx;

    @GET
    @AuthzRead                       // dalla pmr-common-library
    @Path("/prefix_entita_operazione")
    public Response metodoCrud() {
        long   start       = System.nanoTime();
        String kl          = RequestCtx.kl(ctx);
        String tid         = RequestCtx.tid(ctx);
        boolean modAsync   = RequestCtx.modAsync(ctx);
        String processType = RequestCtx.processType(ctx);
        final String path  = "/prefix_entita_operazione";

        try {
            return Utility.okOrEmpty(list, path, kl, tid, modAsync, processType, start);
        } catch (IllegalArgumentException e) {
            return Utility.badRequest(e.getMessage(), path, kl, tid, modAsync, processType, start);
        } catch (RemoteCallException e) {
            return Utility.badGateway(e, path, kl, tid, modAsync, processType, start);
        }
    }
}
```

### Resource DataGateway (senza @AuthzRead/@AuthzWrite — sicurezza delegata al Frontiera)

```java
@Path("/entita")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@Blocking
@LogPmr
public class XxxResource {

    @Inject XxxService service;
    @Context ContainerRequestContext ctx;

    @GET
    public Response getAll() {
        long start = System.nanoTime();
        final String path = "/entita";
        String kl = RequestCtx.kl(ctx); String tid = RequestCtx.tid(ctx);
        boolean modAsync = RequestCtx.modAsync(ctx); String pt = RequestCtx.processType(ctx);
        List<XxxDTO> list = service.getAll();
        return Utility.okOrEmpty(list, path, kl, tid, modAsync, pt, start);
    }
}
```

### Service Frontiera (delega al client DG)

```java
@ApplicationScoped
public class XxxService {
    @Inject @RestClient XxxDgClient client;
    @Inject ObjectMapper objectMapper;

    public List<XxxDTO> getAll(String keyLogic, String transactionId,
                                boolean modAsync, String processType) {
        try (Response resp = client.getAll(keyLogic, transactionId, modAsync, processType)) {
            int status = resp.getStatus();
            if (status == 204) return List.of();
            if (status == 200) return readList(resp.readEntity(String.class));
            throw new RemoteCallException("Errore HTTP " + status);
        }
    }
}
```

### Service DataGateway (accede al DB tramite repository + mapper)

```java
@ApplicationScoped
public class XxxService {
    @Inject XxxRepository repository;
    @Inject XxxMapper mapper;

    public List<XxxDTO> getAll() {
        return mapper.toDtoList(repository.findAllActive());
    }

    @Transactional
    public XxxDTO save(XxxDTO dto) {
        Optional<XxxEntity> existing = repository.findByCode(dto.code());
        XxxEntity entity = existing.orElseGet(() -> mapper.toEntity(dto));
        if (existing.isPresent()) mapper.updateEntityFromDto(dto, entity);
        else repository.persist(entity);
        return mapper.toDto(entity);
    }
}
```

### Entity DataGateway

```java
@Entity
@Audited                             // Hibernate Envers
@Table(name = "NOME_TABELLA")
public class XxxEntity extends PanacheEntityBase {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(nullable = false, updatable = false)
    private Long id;

    @NotBlank
    @Column(name = "CODE", nullable = false, length = 100)
    private String code;

    @NotNull
    @Column(name = "IS_DELETED", nullable = false)
    private Integer isDeleted = 0;
    // ... getters/setters
}
```

### Repository DataGateway

```java
@ApplicationScoped
public class XxxRepository implements PanacheRepository<XxxEntity> {
    @Inject EntityManager em;

    public Optional<XxxEntity> findByCode(String code) {
        return find("code = ?1 AND isDeleted = 0", code).firstResultOptional();
    }
}
```

### Mapper DataGateway (MapStruct)

```java
@Mapper(componentModel = MappingConstants.ComponentModel.JAKARTA)
public interface XxxMapper {
    XxxDTO toDto(XxxEntity entity);
    @Mapping(target = "id", ignore = true)
    XxxEntity toEntity(XxxDTO dto);
    List<XxxDTO> toDtoList(List<XxxEntity> entities);
    @Mapping(target = "id", ignore = true)
    void updateEntityFromDto(XxxDTO dto, @MappingTarget XxxEntity entity);
}
```

### DTO Frontiera (Lombok class)

```java
@Data @NoArgsConstructor @AllArgsConstructor @Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(name = "XxxDTO", description = "...")
public class XxxDTO {
    private Long id;
    // campi...
}
```

### DTO DataGateway (Java record + @Builder)

```java
@Builder
public record XxxDTO(
    String code,
    String description,
    Integer status,
    LocalDateTime actionDate,
    String userAction,
    Integer isDeleted
) {}
```

### Client REST (solo Frontiera)

```java
@Produces(MediaType.APPLICATION_JSON)
@RegisterRestClient(configKey = "<service-name>-dg-client")
public interface XxxDgClient {
    @GET @Path("/xxx")
    Response getAll(
        @HeaderParam(Constants.Headers.KEYLOGIC)       String keyLogic,
        @HeaderParam(Constants.Headers.TRANSACTION_ID) String transactionId,
        @HeaderParam(Constants.Headers.MOD_ASYNC)
        @DefaultValue("false") boolean modAsync,
        @HeaderParam(Constants.Headers.PROCESS_TYPE)   String processType
    );
}
```

---

## Headers HTTP obbligatori (sempre propagati)

| Header | Costante | Descrizione |
|---|---|---|
| `keyLogic` | `Constants.Headers.KEYLOGIC` | Chiave correlazione tecnica |
| `transactionId` | `Constants.Headers.TRANSACTION_ID` | ID transazione |
| `modAsync` | `Constants.Headers.MOD_ASYNC` | Modalità asincrona (default: false) |
| `processType` | `Constants.Headers.PROCESS_TYPE` | Tipo processo (GUI/FLUSSO/N/A) |

---

## Regole di naming

| Elemento | Convenzione | Esempio |
|---|---|---|
| Service name | kebab-case | `gestione-contratti` |
| DataGateway name | kebab-case + `-dg` | `gestione-contratti-dg` |
| Package | tutto minuscolo, no trattini | `it.eng.snam.pmr.gestionecontratti` |
| Classi | PascalCase + suffisso | `GestioneContrattiService` |
| Path REST (Frontiera) | `prefix_entita_operazione` | `/gc_contratti_getall` |
| Path REST (DataGateway) | `/<nomebreve>` | `/gestionecontratti` |
| Client config key | `<service-name>-dg-client` | `gestione-contratti-dg-client` |
| Topic Kafka | `pmr-<nomebreve>` | `pmr-gestionecontratti` |
| Tabella DB | MAIUSCOLO | `GESTIONE_CONTRATTI` |
| Tabella audit | MAIUSCOLO + `_AUD` | `GESTIONE_CONTRATTI_AUD` |

---

## application.properties: sezioni obbligatorie

### Frontiera

1. `quarkus.application.name` / `quarkus.http.port`
2. Logging con MDC pattern (API, TN, KL, MK, PT)
3. Redis (`quarkus.redis.hosts`)
4. Kafka producer (`mp.messaging.outgoing.kafka-out.*`)
5. Kafka consumer **commentato** (da abilitare se necessario)
6. Security HTTP policy (`quarkus.http.auth.permission.*`) + OIDC disabilitato
7. Health + Metrics + OpenAPI
8. Client REST (`<service>-dg-client/mp-rest/url`)
9. Profilo `%dev` con security.authz.bypass e Kafka PLAINTEXT

### DataGateway (aggiunge rispetto a Frontiera)

10. Datasource MSSQL (`quarkus.datasource.*`)
11. Hibernate ORM (`quarkus.hibernate-orm.database.generation=none`)
12. Flyway (`quarkus.flyway.enabled=false`, `migrate-at-start=false`)
13. Kafka consumer **attivo** (`mp.messaging.incoming.*`)
14. Scheduler (`quarkus.scheduler.enabled=true` + `cron.*`)
15. `%dev.quarkus.hibernate-orm.enabled=true`

---

## Quando l'utente chiede di aggiungere una nuova entità

### Frontiera
1. Crea `<Entita>DTO.java` in `dto/` (Lombok class)
2. Crea `<Entita>DgClient.java` in `client/` con il `configKey` del servizio DG
3. Crea `<Entita>Service.java` in `service/` con pattern try-with-resources su Response
4. Crea `<Entita>Resource.java` in `resource/` con `@AuthzRead`/`@AuthzWrite`, `@LogPmr`, `@Blocking`
5. Aggiungi il topic Kafka in `Constants.Topic` se necessario
6. Aggiorna `application.properties` se il client punta a un servizio diverso

### DataGateway
1. Crea `<Entita>Entity.java` in `domain/` (PanacheEntityBase + @Entity + @Audited)
2. Crea `<Entita>Repository.java` in `repository/` (PanacheRepository)
3. Crea `<Entita>Mapper.java` in `mapper/` (MapStruct JAKARTA)
4. Crea `<Entita>DTO.java` in `dto/` (record + @Builder)
5. Crea `<Entita>Service.java` in `service/` con @Transactional sui metodi write
6. Crea `<Entita>Resource.java` in `resource/` con `@LogPmr`, `@Blocking` (NO @AuthzRead/@AuthzWrite)
7. Aggiungi la migrazione SQL in `db/migration/`
8. Aggiungi handler Kafka in `KafkaGenericConsumer.java`

---

## Regole importanti

### Comuni a entrambi i tipi
- **SEMPRE** usare `@Blocking` nelle Resource (il progetto usa Quarkus REST reattivo)
- **SEMPRE** usare `Utility.*` per costruire le Response (mai `Response.ok()` diretto)
- Logger: usare `org.jboss.logging.Logger` nelle Resource/Service, `org.slf4j.Logger` in TopicService

### Solo Frontiera
- **NON** usare `@Transactional` (non c'è JPA)
- **NON** usare `@Inject SecurityIdentity` direttamente nelle Resource: sicurezza gestita da `pmr-common-library` tramite `@AuthzRead`/`@AuthzWrite`
- **IN DEV** usare `%dev.security.authz.bypass=true` per testare i filter senza authorization service attivo
- **SEMPRE** propagare i 4 header (kl, tid, modAsync, processType) nelle chiamate ai client
- **SEMPRE** usare `try-with-resources` sui client REST (`try (Response resp = client.xxx()) { ... }`)

### Solo DataGateway
- **NON** usare `@AuthzRead`/`@AuthzWrite` nelle Resource: il DG è un servizio interno, la sicurezza è gestita dal Frontiera
- **SEMPRE** aggiungere `@Transactional` sui metodi di scrittura nel Service
- **SEMPRE** ignorare `id` nel mapper (`@Mapping(target = "id", ignore = true)`)
- **SEMPRE** usare soft-delete (`IS_DELETED = 1`) invece di cancellazione fisica
- **SEMPRE** aggiornare `ACTION_DATE` e `USER_ACTION` su ogni modifica
- Il consumer Kafka deve usare `@Acknowledgment(Acknowledgment.Strategy.MANUAL)` e fare `message.ack()` anche in caso di errore


### Solo microservizio (usa pmr-common-library di default)
```bash
python3 ./scaffold_quarkus.py \
  --service-name  <nome-servizio> \
  --base-package  <package.java.base> \
  --output-dir    .
```

### Microservizio + libreria custom (generate e collegate automaticamente)
```bash
python3 ./scaffold_quarkus.py \
  --service-name  <nome-servizio> \
  --base-package  <package.java.base> \
  --lib-name      <nome-libreria> \
  --lib-package   <package.libreria> \
  --output-dir    .
```

### Solo libreria
```bash
python3 ./scaffold_quarkus.py \
  --lib-only \
  --lib-name    <nome-libreria> \
  --lib-package <package.libreria> \
  --output-dir  .
```

---

## Stack tecnologico (immutabile)

| Tecnologia | Versione |
|---|---|
| Java | 21 |
| Quarkus BOM | 3.9.2 |
| Lombok | 1.18.32 |
| MapStruct | 1.6.3 |
| pmr-common-library | 1.0.0-SNAPSHOT |

### Dipendenze sempre presenti

- `quarkus-rest` + `quarkus-rest-jackson` + `quarkus-rest-client-jackson`
- `quarkus-hibernate-validator`
- `quarkus-messaging-kafka` + `quarkus-smallrye-reactive-messaging-kafka`
- `quarkus-redis-client` + `quarkus-cache`
- `quarkus-oidc`
- `quarkus-smallrye-health`
- `quarkus-micrometer-registry-prometheus`
- `quarkus-smallrye-openapi`
- `quarkus-smallrye-fault-tolerance`
- `quarkus-junit5-mockito` + `rest-assured` (scope test)

---

## Struttura package obbligatoria

```
<basePackage>/
├── config/       ApplicationConfig.java, OpenApiConfig.java
├── filter/       MdcHeadersFilter.java, GlobalHeadersOpenApiFilter.java
├── health/       ApplicationHealthCheck.java
├── kafka/        KafkaGenericProducer.java, KafkaGenericConsumer.java
├── service/      TopicService.java, <Entità>Service.java...
├── resource/     <Entità>Resource.java...
├── client/       <Entità>DgClient.java...
├── dto/          <Entità>DTO.java...
├── exception/    RemoteCallException.java, RetryableRemoteException.java
├── response/     GenericResponse.java, ResponseStatus.java
└── utils/        Constants.java, RequestCtx.java, Utility.java,
                  JsonUtils.java, MessageTypeEnum.java
```

---

## Pattern obbligatori per le classi

### Resource (Controller REST)

```java
@Path("/")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@Blocking
@LogPmr                              // dalla pmr-common-library
public class XxxResource {

    @Inject XxxService service;
    @Context ContainerRequestContext ctx;

    @GET
    @AuthzRead                       // dalla pmr-common-library
    @Path("/prefix_entita_operazione")
    public Response metodoCrud() {
        long   start       = System.nanoTime();
        String kl          = RequestCtx.kl(ctx);
        String tid         = RequestCtx.tid(ctx);
        boolean modAsync   = RequestCtx.modAsync(ctx);
        String processType = RequestCtx.processType(ctx);
        final String path  = "/prefix_entita_operazione";

        try {
            // logica...
            return Utility.okOrEmpty(list, path, kl, tid, modAsync, processType, start);
        } catch (IllegalArgumentException e) {
            return Utility.badRequest(e.getMessage(), path, kl, tid, modAsync, processType, start);
        } catch (RemoteCallException e) {
            return Utility.badGateway(e, path, kl, tid, modAsync, processType, start);
        }
    }
}
```

### Service

```java
@ApplicationScoped
public class XxxService {
    @Inject @RestClient XxxDgClient client;
    @Inject ObjectMapper objectMapper;

    public List<XxxDTO> getAll(String keyLogic, String transactionId,
                                boolean modAsync, String processType) {
        try (Response resp = client.getAll(keyLogic, transactionId, modAsync, processType)) {
            int status = resp.getStatus();
            if (status == 204) return List.of();
            if (status == 200) return readList(resp.readEntity(String.class));
            throw new RemoteCallException("Errore HTTP " + status);
        }
    }
}
```

### Client REST

```java
@Produces(MediaType.APPLICATION_JSON)
@RegisterRestClient(configKey = "<service-name>-dg-client")
public interface XxxDgClient {
    @GET @Path("/xxx")
    Response getAll(
        @HeaderParam(Constants.Headers.KEYLOGIC)       String keyLogic,
        @HeaderParam(Constants.Headers.TRANSACTION_ID) String transactionId,
        @HeaderParam(Constants.Headers.MOD_ASYNC)
        @DefaultValue("false") boolean modAsync,
        @HeaderParam(Constants.Headers.PROCESS_TYPE)   String processType
    );
}
```

### DTO

```java
@Data @NoArgsConstructor @AllArgsConstructor @Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(name = "XxxDTO", description = "...")
public class XxxDTO {
    private Long id;
    // campi...
}
```

---

## Headers HTTP obbligatori (sempre propagati)

| Header | Costante | Descrizione |
|---|---|---|
| `keyLogic` | `Constants.Headers.KEYLOGIC` | Chiave correlazione tecnica |
| `transactionId` | `Constants.Headers.TRANSACTION_ID` | ID transazione |
| `modAsync` | `Constants.Headers.MOD_ASYNC` | Modalità asincrona (default: false) |
| `processType` | `Constants.Headers.PROCESS_TYPE` | Tipo processo (GUI/FLUSSO/N/A) |

---

## Regole di naming

| Elemento | Convenzione | Esempio |
|---|---|---|
| Service name | kebab-case | `gestione-contratti` |
| Package | tutto minuscolo, no trattini | `it.eng.snam.pmr.gestionecontratti` |
| Classi | PascalCase + suffisso | `GestioneContrattiService` |
| Path REST | `prefix_entita_operazione` | `/gc_contratti_getall` |
| Client config key | `<service-name>-dg-client` | `gestione-contratti-dg-client` |
| Topic Kafka | `pmr-<nomebreve>` | `pmr-gestionecontratti` |

---

## application.properties: sezioni obbligatorie

Ogni microservizio deve avere configurate:
1. `quarkus.application.name` / `quarkus.http.port`
2. Logging con MDC pattern (API, TN, KL, MK, PT)
3. Redis (`quarkus.redis.hosts`)
4. Kafka producer (`mp.messaging.outgoing.kafka-out.*`)
5. Security HTTP policy (`quarkus.http.auth.permission.*`) + OIDC disabilitato
6. Health + Metrics + OpenAPI
7. Client REST (`<service>-dg-client/mp-rest/url`)
8. Profilo `%dev` con security.authz.bypass e Kafka PLAINTEXT

---

## Quando l'utente chiede di aggiungere una nuova entità

1. Crea `<Entita>DTO.java` in `dto/`
2. Crea `<Entita>DgClient.java` in `client/` con il `configKey` del servizio DG
3. Crea `<Entita>Service.java` in `service/` con pattern try-with-resources su Response
4. Crea `<Entita>Resource.java` in `resource/` con `@AuthzRead`/`@AuthzWrite`, `@LogPmr`, `@Blocking`
5. Aggiungi il topic Kafka in `Constants.Topic` se necessario
6. Aggiorna `application.properties` se il client punta a un servizio diverso

---

## Regole importanti

- **NON** usare `@Transactional` (non c'è JPA nel progetto)
- **NON** usare `@Inject SecurityIdentity` direttamente nelle Resource: la sicurezza è gestita dalla `pmr-common-library` tramite `@AuthzRead`/`@AuthzWrite`
- **IN DEV** usare `%dev.security.authz.bypass=true` per testare i filter senza authorization service attivo
- **SEMPRE** usare `@Blocking` nelle Resource (il progetto usa Quarkus REST reattivo)
- **SEMPRE** usare `Utility.*` per costruire le Response (mai `Response.ok()` diretto)
- **SEMPRE** propagare i 4 header (kl, tid, modAsync, processType) nelle chiamate ai client
- **SEMPRE** usare `try-with-resources` sui client REST (`try (Response resp = client.xxx()) { ... }`)
- Logger: usare `org.jboss.logging.Logger` nelle Resource/Service, `org.slf4j.Logger` in TopicService
