#!/usr/bin/env python3
"""
Quarkus Microservice + Common Library Scaffold Generator
Genera microservizio Quarkus e/o libreria comune seguendo i pattern PMR.

Utilizzo:
  # Solo microservizio (usa pmr-common-library di default)
  python3 scaffold_quarkus.py --service-name my-svc --base-package it.eng.myorg.mysvc

  # Microservizio + libreria custom (generate e collegate automaticamente)
  python3 scaffold_quarkus.py --service-name my-svc --base-package it.eng.myorg.mysvc \
                              --lib-name my-common-lib --lib-package it.eng.myorg.common

  # Solo libreria
  python3 scaffold_quarkus.py --lib-only --lib-name my-common-lib --lib-package it.eng.myorg.common

  # Con output-dir custom
  python3 scaffold_quarkus.py ... --output-dir /path/to/projects
"""

import argparse
import re
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def to_class_prefix(name: str) -> str:
    """'my-new-service' → 'MyNewService'"""
    return "".join(p.capitalize() for p in re.split(r"[-_]", name))


def to_short(name: str) -> str:
    """'my-new-service' → 'mynewservice'"""
    return re.sub(r"[-_]", "", name.lower())


def pkg_to_path(package: str) -> str:
    return package.replace(".", "/")


def parent_pkg(package: str) -> str:
    """'it.eng.myorg.common' → 'it.eng.myorg'"""
    return ".".join(package.split(".")[:-1])


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  ✔  {path}")


# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT library coordinates (pmr-common-library originale)
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_LIB_GROUP    = "it.eng.snam.pmr"
DEFAULT_LIB_ARTIFACT = "pmr-common-library"
DEFAULT_LIB_PKG      = "it.eng.snam.pmr.common"


# ═════════════════════════════════════════════════════════════════════════════
# GENERATORS — MICROSERVIZIO
# ═════════════════════════════════════════════════════════════════════════════

def gen_pom(sn, pkg, lib_group, lib_artifact):
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">

    <modelVersion>4.0.0</modelVersion>

    <groupId>{pkg}</groupId>
    <artifactId>{sn}</artifactId>
    <version>1.0.0-SNAPSHOT</version>

    <properties>
        <java.version>21</java.version>
        <lombok.version>1.18.32</lombok.version>
        <compiler-plugin.version>3.13.0</compiler-plugin.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <maven-surefire-plugin.version>3.2.5</maven-surefire-plugin.version>
        <quarkus.platform.group-id>io.quarkus.platform</quarkus.platform.group-id>
        <quarkus.platform.artifact-id>quarkus-bom</quarkus.platform.artifact-id>
        <quarkus.platform.version>3.9.2</quarkus.platform.version>
        <mapstruct.version>1.6.3</mapstruct.version>
        <sonar.sources>
            src/main/java/{pkg_to_path(pkg)}/resource,src/main/java/{pkg_to_path(pkg)}/service,src/main/java/{pkg_to_path(pkg)}/utils
        </sonar.sources>
        <sonar.tests>src/test</sonar.tests>
        <sonar.java.coveragePlugin>jacoco</sonar.java.coveragePlugin>
        <sonar.dynamicAnalysis>reuseReports</sonar.dynamicAnalysis>
        <sonar.language>java</sonar.language>
        <argLine/>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>${{quarkus.platform.group-id}}</groupId>
                <artifactId>${{quarkus.platform.artifact-id}}</artifactId>
                <version>${{quarkus.platform.version}}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <!-- Common Library -->
        <dependency>
            <groupId>{lib_group}</groupId>
            <artifactId>{lib_artifact}</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>
        <!-- REST -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-rest</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-rest-jackson</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-rest-client-jackson</artifactId></dependency>
        <!-- VALIDATION -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-hibernate-validator</artifactId></dependency>
        <!-- KAFKA -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-messaging-kafka</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-smallrye-reactive-messaging-kafka</artifactId></dependency>
        <!-- REDIS -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-redis-client</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-cache</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-jackson</artifactId></dependency>
        <!-- SECURITY -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-oidc</artifactId></dependency>
        <!-- OBSERVABILITY -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-smallrye-health</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-micrometer-registry-prometheus</artifactId></dependency>
        <!-- OPENAPI -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-smallrye-openapi</artifactId></dependency>
        <!-- MAPSTRUCT -->
        <dependency>
            <groupId>org.mapstruct</groupId><artifactId>mapstruct</artifactId>
            <version>${{mapstruct.version}}</version>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId><artifactId>lombok</artifactId>
            <version>${{lombok.version}}</version><scope>provided</scope>
        </dependency>
        <!-- FAULT TOLERANCE -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-smallrye-fault-tolerance</artifactId></dependency>
        <!-- TEST -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-junit5-mockito</artifactId><scope>test</scope></dependency>
        <dependency><groupId>io.rest-assured</groupId><artifactId>rest-assured</artifactId><scope>test</scope></dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>io.quarkus</groupId><artifactId>quarkus-maven-plugin</artifactId>
                <version>${{quarkus.platform.version}}</version>
                <executions><execution><goals><goal>build</goal></goals></execution></executions>
            </plugin>
            <plugin>
                <artifactId>maven-compiler-plugin</artifactId><version>${{compiler-plugin.version}}</version>
                <configuration>
                    <release>${{java.version}}</release>
                    <annotationProcessorPaths>
                        <path><groupId>org.mapstruct</groupId><artifactId>mapstruct-processor</artifactId><version>${{mapstruct.version}}</version></path>
                        <path><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><version>${{lombok.version}}</version></path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId><artifactId>maven-surefire-plugin</artifactId>
                <version>${{maven-surefire-plugin.version}}</version>
                <configuration>
                    <argLine>@{{argLine}} -Djava.util.logging.manager=org.jboss.logmanager.LogManager -XX:+EnableDynamicAgentLoading</argLine>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.jacoco</groupId><artifactId>jacoco-maven-plugin</artifactId><version>0.8.14</version>
                <executions>
                    <execution><id>prepare-agent</id><goals><goal>prepare-agent</goal></goals><phase>initialize</phase></execution>
                    <execution><id>report</id><goals><goal>report</goal></goals><phase>verify</phase></execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
"""


def gen_application_properties(sn, pkg, lib_pkg):
    short     = to_short(sn)
    client_key = f"{sn}-dg-client"
    return f"""\
############################################
# QUARKUS CORE
############################################
quarkus.application.name={sn}
quarkus.http.root-path=${{kapp:prefix}}
quarkus.http.port=${{QUARKUS_PORT:8090}}
quarkus.package.output-name={sn}

############################################
# LOGGING - GLOBAL
############################################
quarkus.log.console.enable=true
quarkus.log.level=${{LOG_LEVEL_ROOT_CONSOLE:INFO}}
quarkus.log.category."io.quarkus.confluent".level=ERROR
quarkus.log.console.format=[%5p] %d{{yyyy-MM-dd HH:mm:ss.SSS}} API:%X{{API}} TRANS-ID:%X{{TN}} KEY-LOGIC:%X{{KL}} MESSAGE-KEY:%X{{MK}} PROCESS-TYPE:%X{{PT}} [%t] %c{{1}} - %s%e%n
quarkus.console.color=true

############################################
# CATEGORY LOGGERS
############################################
quarkus.log.category."{pkg}.service".level=${{LOG_LEVEL_SERVICE_CONSOLE:INFO}}
quarkus.log.category."{pkg}.resource".level=${{LOG_LEVEL_CONTROLLER_CONSOLE:INFO}}
quarkus.log.category."{lib_pkg}.interceptor".level=INFO

############################################
# REDIS
############################################
quarkus.redis.hosts=${{REDIS_HOSTS:redis://localhost:6379}}

############################################
# APP CACHE
############################################
app.cache.redis.enabled=true
app.cache.redis.prefix=cache
cache.{short}.sample.ttl-seconds=${{CACHE_{short.upper()}_SAMPLE_TTL:300}}

############################################
# KAFKA
############################################
kafka.bootstrap.servers=${{KAFKA_BOOTSTRAP_SERVERS:localhost:${{KAFKA_SERVER_PORT:9092}}}}
kafka-prefix.topics=${{KAFKA_TOPIC_PREFIX:prefix}}
kafka.security.protocol=SASL_SSL
kafka.sasl.mechanism=PLAIN
kafka.sasl.jaas.username=${{KAFKA_API_KEY:XXXXXXXXXX}}
kafka.sasl.jaas.password=${{KAFKA_API_SECRET:YYYYYYYYYY}}
kafka.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="${{kafka.sasl.jaas.username}}" password="${{kafka.sasl.jaas.password}}";
kafka.request.timeout.ms=30000
kafka.connections.max.idle.ms=540000
kafka.reconnect.backoff.ms=1000
kafka.reconnect.backoff.max.ms=10000
kafka.socket.keepalive.enable=true

############################################
# KAFKA PRODUCER
############################################
mp.messaging.outgoing.kafka-out.connector=smallrye-kafka
mp.messaging.outgoing.kafka-out.bootstrap.servers=${{kafka.bootstrap.servers}}
mp.messaging.outgoing.kafka-out.key.serializer=org.apache.kafka.common.serialization.StringSerializer
mp.messaging.outgoing.kafka-out.value.serializer=org.apache.kafka.common.serialization.StringSerializer
mp.messaging.outgoing.kafka-out.acks=all
mp.messaging.outgoing.kafka-out.retries=3

############################################
# KAFKA CONSUMER (DA CONFIGURARE)
############################################
#mp.messaging.incoming.kafka-in.connector=smallrye-kafka
#mp.messaging.incoming.kafka-in.bootstrap.servers=${{kafka.bootstrap.servers}}
#mp.messaging.incoming.kafka-in.group.id=groupId-{sn}
#mp.messaging.incoming.kafka-in.auto.offset.reset=earliest
#mp.messaging.incoming.kafka-in.value.deserializer=org.apache.kafka.common.serialization.StringDeserializer
#mp.messaging.incoming.kafka-in.enable.auto.commit=false
#mp.messaging.incoming.kafka-in.max.poll.records=1
#mp.messaging.incoming.kafka-in.topic=${{kafka-prefix.topics}}-pmr-{short}

############################################
# SECURITY - HTTP policy
############################################
# Tutte le path pubbliche: la security applicativa è gestita da AuthzReadFilter/AuthzWriteFilter.
quarkus.http.auth.permission.public.paths=/*
quarkus.http.auth.permission.public.policy=permit

############################################
# SECURITY - OIDC
############################################
# OIDC disabilitato: la validazione JWT è delegata all'authorization service esterno.
quarkus.oidc.enabled=false
quarkus.oidc.auth-server-url=${{OIDC_AUTH_SERVER_URL:https://sso.example.com/auth/realms/PMR}}
quarkus.oidc.client-id=${{OIDC_CLIENT_ID:quarkus-client}}
quarkus.oidc.credentials.secret=${{OIDC_SECRET:mysecret}}

############################################
# AUTHORIZATION (common library)
############################################
authorization-client/mp-rest/url=${{AUTHZ_URL:http://localhost:8090/authorization}}
authorization-client/mp-rest/connectTimeout=2000
authorization-client/mp-rest/readTimeout=3000

############################################
# OBSERVABILITY
############################################
quarkus.smallrye-health.root-path=/health
quarkus.micrometer.export.prometheus.path=/metrics

############################################
# OPENAPI
############################################
quarkus.swagger-ui.always-include=true
quarkus.swagger-ui.path=/swagger
quarkus.smallrye-openapi.path=/openapi
mp.openapi.filter={pkg}.filter.GlobalHeadersOpenApiFilter

############################################
# CLIENT REST
############################################
{client_key}/mp-rest/url=${{SERVICE_DG_URL:http://localhost:8091}}
{client_key}/mp-rest/connectTimeout=10000
{client_key}/mp-rest/readTimeout=30000

############################################
# PMR COMMON LIBRARY - CDI INDEX
############################################
quarkus.index-dependency.pmr-common.group-id=it.eng.snam.pmr
quarkus.index-dependency.pmr-common.artifact-id=pmr-common-library

############################################
# DEV PROFILE
############################################
%dev.quarkus.oidc.enabled=false
%dev.security.enabled=true
%dev.security.authz.bypass=true
%dev.kafka.bootstrap.servers=localhost:${{KAFKA_SERVER_PORT:9092}}
%dev.kafka.security.protocol=PLAINTEXT
%dev.kafka.topics.auto-create=true
"""


def gen_application_test_properties_svc(sn):
    return f"""\
quarkus.oidc.enabled=false
quarkus.http.auth.permission.public.paths=/*
quarkus.http.auth.permission.public.policy=permit
security.enabled=false
quarkus.kafka.devservices.enabled=false
quarkus.apicurio-registry.devservices.enabled=false
kafka.bootstrap.servers=localhost:9092
kafka.security.protocol=PLAINTEXT
quarkus.redis.hosts=redis://localhost:6379
quarkus.http.test-port=0
quarkus.log.level=INFO
"""


def gen_constants(pkg, sn):
    short = to_short(sn)
    topic_const = f"{short.upper()}_TOPIC"
    topic_val   = f"{short}"
    return f"""\
package {pkg}.utils;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public interface Constants {{

    String TIMESTAMP_FORMAT = "yyyyMMddHHmmssSSS";
    String MSG_ERROR = "Error";

    interface Headers {{
        String TRANSACTION_ID = "TRANSACTION-ID";
        String KEYLOGIC       = "KEY-LOGIC";
        String MOD_ASYNC      = "MOD-ASYNC";
        String PROCESS_TYPE   = "PROCESS-TYPE";
        String JWT            = "JWT";
        String AUTHORIZATION  = "Authorization";
    }}

    interface LogParams {{
        String TN = "TN";
        String KL = "KL";
        String API = "API";
        String MK = "MK";
        String PT = "PT";
        String MA = "MA";
    }}

    interface MEDIATYPE {{
        String APP_JSON = "application/json";
    }}

    interface Topic {{
        String {topic_const} = "{topic_val}";

        static List<String> getAllTopicsValue() throws IllegalArgumentException, IllegalAccessException {{
            List<Field> fields = Arrays.asList(Constants.Topic.class.getDeclaredFields());
            List<String> topics = new ArrayList<>();
            for (Field field : fields) {{
                Object object = field.get(null);
                if (object instanceof String) topics.add((String) object);
            }}
            return topics;
        }}
    }}
}}
"""


def gen_request_ctx(pkg):
    return f"""\
package {pkg}.utils;

import {pkg}.filter.MdcHeadersFilter;
import jakarta.ws.rs.container.ContainerRequestContext;

public final class RequestCtx {{
    private RequestCtx() {{}}

    public static String kl(ContainerRequestContext ctx)  {{ return (String) ctx.getProperty(MdcHeadersFilter.PROP_KL); }}
    public static String tid(ContainerRequestContext ctx) {{ return (String) ctx.getProperty(MdcHeadersFilter.PROP_TID); }}
    public static boolean modAsync(ContainerRequestContext ctx) {{
        Object v = ctx.getProperty(MdcHeadersFilter.PROP_MOD_ASYNC);
        return (v instanceof Boolean b) && b;
    }}
    public static String processType(ContainerRequestContext ctx) {{
        Object o = ctx.getProperty("CTX_PROCESS_TYPE");
        return o != null ? o.toString() : "N/A";
    }}
}}
"""


def gen_utility(pkg):
    return f"""\
package {pkg}.utils;

import java.time.Duration;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import {pkg}.exception.RemoteCallException;
import {pkg}.filter.RequestHeadersContext;
import {pkg}.response.GenericResponse;
import {pkg}.response.GenericResponse.Message;
import {pkg}.response.ResponseStatus;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.core.Response;

@ApplicationScoped
public class Utility {{

    @Inject
    RequestHeadersContext headersCtx;

    // =========================
    // Static helpers
    // =========================

    public static String defaultUuidIfBlank(String v) {{
        return (v == null || v.isBlank()) ? UUID.randomUUID().toString() : v;
    }}
    public static boolean parseBooleanOrDefault(String v, boolean defaultValue) {{
        if (v == null || v.isBlank()) return defaultValue;
        String s = v.trim().toLowerCase();
        if ("true".equals(s)) return true;
        if ("false".equals(s)) return false;
        return defaultValue;
    }}
    public static String defaultIfBlank(String v, String def) {{
        return (v == null || v.trim().isEmpty()) ? def : v;
    }}
    public static long elapsedMs(long s) {{ return (System.nanoTime() - s) / 1_000_000; }}
    public static String safe(Object v) {{
        if (v == null) return "null";
        String s = String.valueOf(v).trim();
        if (s.isEmpty()) return "blank";
        return s.length() > 120 ? s.substring(0, 120) + "..." : s;
    }}

    // =========================
    // Context helpers
    // =========================

    private String currentPath() {{
        String p = (headersCtx != null) ? headersCtx.getPath() : null;
        return (p == null || p.isBlank()) ? "N/A" : p;
    }}

    private long startNanos() {{
        long s = (headersCtx != null) ? headersCtx.getStartNanos() : 0L;
        return (s > 0L) ? s : System.nanoTime();
    }}

    private String executionTime() {{
        return Duration.ofNanos(System.nanoTime() - startNanos()).toMillis() + "ms";
    }}

    // =========================
    // Common headers
    // =========================

    private Response.ResponseBuilder withCommonHeaders(Response.ResponseBuilder rb) {{
        return rb
            .header(Constants.Headers.KEYLOGIC,       headersCtx.getKeyLogic())
            .header(Constants.Headers.TRANSACTION_ID, headersCtx.getTransactionId())
            .header(Constants.Headers.MOD_ASYNC,      String.valueOf(headersCtx.isModAsync()))
            .header(Constants.Headers.PROCESS_TYPE,   headersCtx.getProcessType());
    }}

    // =========================
    // Internal builder
    // =========================

    private static <T> GenericResponse<T> baseGeneric(String path) {{
        GenericResponse<T> gr = new GenericResponse<>();
        gr.setTimestamp(OffsetDateTime.now().toString());
        gr.setPath(path);
        return gr;
    }}

    // =========================
    // 200 OK
    // =========================

    public <T> Response ok(T data) {{
        String path = currentPath();
        GenericResponse<T> gr = baseGeneric(path);
        gr.setData(data);
        gr.setExecutionTime(executionTime());
        if (data instanceof List<?> l) gr.setNumberOfElements(l.size());
        return withCommonHeaders(Response.ok(gr)).build();
    }}

    public <T> Response inProgress(T data) {{
        String path = currentPath();
        GenericResponse<T> gr = baseGeneric(path);
        gr.setData(data);
        gr.setExecutionTime(executionTime());
        gr.setStatus(ResponseStatus.IN_ELABORAZIONE.toString());
        if (data instanceof List<?> l) gr.setNumberOfElements(l.size());
        return withCommonHeaders(Response.ok(gr)).build();
    }}

    public <T> Response okWithMessageCustom(T data, Message msg) {{
        String path = currentPath();
        GenericResponse<T> gr = baseGeneric(path);
        gr.setData(data);
        gr.setExecutionTime(executionTime());
        gr.setMessage(msg);
        if (data instanceof List<?> l) gr.setNumberOfElements(l.size());
        return withCommonHeaders(Response.ok(gr)).build();
    }}

    public <T> Response okEmpty() {{
        String path = currentPath();
        GenericResponse<T> gr = baseGeneric(path);
        gr.setExecutionTime(executionTime());
        gr.setNumberOfElements(0);
        return withCommonHeaders(Response.ok(gr)).build();
    }}

    // =========================
    // 201 CREATED
    // =========================

    public <T> Response created(T data) {{
        String path = currentPath();
        GenericResponse<T> gr = baseGeneric(path);
        gr.setData(data);
        gr.setExecutionTime(executionTime());
        if (data instanceof List<?> l) gr.setNumberOfElements(l.size());
        return withCommonHeaders(Response.status(Response.Status.CREATED).entity(gr)).build();
    }}

    // =========================
    // 404 NOT FOUND
    // =========================

    public <T> Response notFound(String message) {{
        String path = currentPath();
        GenericResponse<T> gr = baseGeneric(path);
        gr.setExecutionTime(executionTime());
        Message m = new Message();
        m.setMessageType("ERROR"); m.setMessageCode("NOT_FOUND"); m.setMessageDescription(message);
        gr.setMessage(m);
        return withCommonHeaders(Response.status(Response.Status.NOT_FOUND).entity(gr)).build();
    }}

    public <T> Response notFoundWithMessageCustom(Message message) {{
        String path = currentPath();
        GenericResponse<T> gr = baseGeneric(path);
        gr.setExecutionTime(executionTime());
        gr.setMessage(message);
        return withCommonHeaders(Response.status(Response.Status.NOT_FOUND).entity(gr)).build();
    }}

    // =========================
    // 400 BAD REQUEST
    // =========================

    public <T> Response badRequest(String message) {{
        String path = currentPath();
        GenericResponse<T> gr = baseGeneric(path);
        gr.setExecutionTime(executionTime());
        Message m = new Message();
        m.setMessageType("ERROR"); m.setMessageCode("BAD_REQUEST"); m.setMessageDescription(message);
        gr.setMessage(m);
        return withCommonHeaders(Response.status(Response.Status.BAD_REQUEST).entity(gr)).build();
    }}

    // =========================
    // 502 BAD GATEWAY
    // =========================

    public <T> Response badGateway(RemoteCallException e) {{
        String path = currentPath();
        GenericResponse<T> gr = baseGeneric(path);
        gr.setExecutionTime(executionTime());
        Message m = new Message();
        m.setMessageType("ERROR"); m.setMessageCode("BAD_GATEWAY"); m.setMessageDescription(e.getMessage());
        gr.setMessage(m);
        return withCommonHeaders(Response.status(Response.Status.BAD_GATEWAY).entity(gr)).build();
    }}

    // =========================
    // 204 NO CONTENT
    // =========================

    public Response noContentOnlyHeaders() {{
        return withCommonHeaders(Response.noContent()).build();
    }}

    // =========================
    // Helper: Optional & List
    // =========================

    public <T> Response okOrNotFound(Optional<T> opt, String notFoundMessage) {{
        if (opt == null || opt.isEmpty()) return notFound(notFoundMessage);
        return ok(opt.get());
    }}

    public <T> Response okOrNotFoundWithCustomMessage(Optional<T> opt, Message customMessage) {{
        if (opt == null || opt.isEmpty()) return notFoundWithMessageCustom(customMessage);
        return okWithMessageCustom(opt.get(), customMessage);
    }}

    public <T> Response okOrEmpty(List<T> list) {{
        if (list == null || list.isEmpty()) return okEmpty();
        return ok(list);
    }}

    public <T> Response okOrEmptyWithCustomMessage(List<T> list, Message customMessage) {{
        if (list == null || list.isEmpty()) return okEmpty();
        return okWithMessageCustom(list, customMessage);
    }}

}}
"""


def gen_json_utils(full_pkg):
    """Genera JsonUtils nel package indicato (full_pkg = package completo, es. it.eng.snam.pmr.common.util)."""
    return f"""\
package {full_pkg};

import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.slf4j.*;
import java.io.IOException;

public class JsonUtils {{
    private static final Logger logger = LoggerFactory.getLogger(JsonUtils.class);
    private static final ObjectMapper mapper = new ObjectMapper();

    private JsonUtils() {{}}

    static {{
        mapper.registerModule(new JavaTimeModule());
        mapper.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
        mapper.setSerializationInclusion(Include.NON_NULL);
        mapper.configure(DeserializationFeature.FAIL_ON_MISSING_CREATOR_PROPERTIES, false);
        mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        mapper.configure(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY, true);
        mapper.enable(DeserializationFeature.ACCEPT_EMPTY_STRING_AS_NULL_OBJECT);
    }}

    public static String writeAsJsonStringWithoutNull(Object obj) {{
        try {{ return obj != null ? mapper.writer().writeValueAsString(obj) : null; }}
        catch (Exception e) {{ logger.error("While trying to convert to JSON String"); return null; }}
    }}

    public static String writeAsJsonPrettyLogStringWithoutNull(Object obj) {{
        try {{ return obj != null ? mapper.writerWithDefaultPrettyPrinter().writeValueAsString(obj) : null; }}
        catch (Exception e) {{ logger.error("While trying to convert to JSON String"); return null; }}
    }}

    public static <T> T getObject(String json, Class<T> clazz) throws IOException {{
        return mapper.readValue(json, clazz);
    }}

    public static <T> T getObject(TypeReference<T> ref, String value) throws IOException {{
        return (value != null && !value.trim().isEmpty()) ? mapper.readValue(value, ref) : null;
    }}
}}
"""


def gen_request_headers_context(pkg):
    return f"""\
package {pkg}.filter;

import jakarta.enterprise.context.RequestScoped;

@RequestScoped
public class RequestHeadersContext {{

    private String keyLogic;
    private String transactionId;
    private boolean modAsync;
    private String processType;
    private String path;
    private long startNanos;

    public String getKeyLogic() {{ return keyLogic; }}
    public void setKeyLogic(String keyLogic) {{ this.keyLogic = keyLogic; }}

    public String getTransactionId() {{ return transactionId; }}
    public void setTransactionId(String transactionId) {{ this.transactionId = transactionId; }}

    public boolean isModAsync() {{ return modAsync; }}
    public void setModAsync(boolean modAsync) {{ this.modAsync = modAsync; }}

    public String getProcessType() {{ return processType; }}
    public void setProcessType(String processType) {{ this.processType = processType; }}

    public String getPath() {{ return path; }}
    public void setPath(String path) {{ this.path = path; }}

    public long getStartNanos() {{ return startNanos; }}
    public void setStartNanos(long startNanos) {{ this.startNanos = startNanos; }}
}}
"""


def gen_rest_client_headers_filter(pkg):
    return f"""\
package {pkg}.filter;

import {pkg}.utils.Constants;
import jakarta.inject.Inject;
import jakarta.ws.rs.client.ClientRequestContext;
import jakarta.ws.rs.client.ClientRequestFilter;
import jakarta.ws.rs.ext.Provider;

@Provider
public class RestClientHeadersFilter implements ClientRequestFilter {{

    @Inject
    RequestHeadersContext ctx;

    @Override
    public void filter(ClientRequestContext requestContext) {{
        requestContext.getHeaders().putSingle(Constants.Headers.KEYLOGIC,       ctx.getKeyLogic());
        requestContext.getHeaders().putSingle(Constants.Headers.TRANSACTION_ID, ctx.getTransactionId());
        requestContext.getHeaders().putSingle(Constants.Headers.MOD_ASYNC,      String.valueOf(ctx.isModAsync()));
        requestContext.getHeaders().putSingle(Constants.Headers.PROCESS_TYPE,   ctx.getProcessType());
    }}
}}
"""


def gen_rest_application(pkg):
    return f"""\
package {pkg}.config;

import jakarta.ws.rs.ApplicationPath;
import jakarta.ws.rs.core.Application;

@ApplicationPath("/")
public class RestApplication extends Application {{
}}
"""


def gen_message_type_enum(pkg):
    return f"""\
package {pkg}.utils;

public enum MessageTypeEnum {{
    OK                  ("Info",  "1"),
    ERROR_GESTITO_SEARCH("Info",  "4"),
    ERROR_GESTITO       (Constants.MSG_ERROR, "2"),
    ERROR_NON_GESTITO   (Constants.MSG_ERROR, "3"),
    ERROR_BUSINESS_LOGIC(Constants.MSG_ERROR, "7");

    private final String messageType;
    private final String messageCode;
    MessageTypeEnum(String t, String c) {{ this.messageType = t; this.messageCode = c; }}
    public String getMessageType() {{ return messageType; }}
    public String getMessageCode() {{ return messageCode; }}
}}
"""





def gen_remote_call_exception(pkg):
    return f"""\
package {pkg}.exception;
public class RemoteCallException extends RuntimeException {{
    private static final long serialVersionUID = 1L;
    public RemoteCallException(String message) {{ super(message); }}
    public RemoteCallException(String message, Throwable cause) {{ super(message, cause); }}
}}
"""


def gen_retryable_remote_exception(pkg):
    return f"""\
package {pkg}.exception;
public class RetryableRemoteException extends RemoteCallException {{
    private static final long serialVersionUID = 1L;
    public RetryableRemoteException(String message) {{ super(message); }}
    public RetryableRemoteException(String message, Throwable cause) {{ super(message, cause); }}
}}
"""


def gen_generic_response(pkg):
    return f"""\
package {pkg}.response;

import java.io.Serializable;
import java.time.OffsetDateTime;
import java.util.List;
import org.eclipse.microprofile.openapi.annotations.media.Schema;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import {pkg}.utils.MessageTypeEnum;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Schema(name = "GenericResponse", description = "Generic API response wrapper")
@JsonInclude(Include.NON_EMPTY)
public class GenericResponse<T> implements Serializable {{
    private static final long serialVersionUID = 5007807046893745317L;
    private T data;
    private String status;
    private String executionTime;
    private String timestamp;
    private Integer numberOfElements;
    private Integer numberOfPages;
    private String path;
    @JsonInclude(Include.NON_NULL)
    private Message message;

    public GenericResponse() {{
        this.timestamp = OffsetDateTime.now().toString();
        this.status = ResponseStatus.ELABORATO.toString();
    }}
    public GenericResponse(T data, String resultDescription) {{ this(); this.data = data; }}

    public void buildMessage(MessageTypeEnum e) {{
        if (message == null) message = new Message();
        message.setMessageType(e.getMessageType()); message.setMessageCode(e.getMessageCode());
    }}
    public void buildMessage(MessageTypeEnum e, String desc, List<String> ph) {{
        if (message == null) message = new Message();
        message.setMessageType(e.getMessageType()); message.setMessageCode(e.getMessageCode());
        message.setMessageDescription(desc); message.setMessagePlaceholder(ph);
    }}

    @Data @NoArgsConstructor @AllArgsConstructor
    @Schema(name = "GenericResponseMessage")
    @JsonInclude(Include.NON_NULL)
    public static class Message implements Serializable {{
        private static final long serialVersionUID = -3699628142644425282L;
        private String messageType;
        private String messageCode;
        private String messageDescription;
        private List<String> messagePlaceholder;
        public Message(String t, String c, List<String> ph) {{ this.messageType=t; this.messageCode=c; this.messagePlaceholder=ph; }}
    }}
}}
"""


def gen_custom_response(pkg):
    return f"""\
package {pkg}.response;

import java.io.Serializable;

import org.eclipse.microprofile.openapi.annotations.media.Schema;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

import {pkg}.response.GenericResponse.Message;
import lombok.Data;

@Data
@Schema(name = "CustomResponse", description = "Response Wrapper with Custom Message")
@JsonInclude(Include.NON_EMPTY)
public class CustomResponse<T> implements Serializable {{

    private static final long serialVersionUID = 5007805106893745317L;

    private T responseData;
    @JsonInclude(Include.NON_NULL)
    private Message message;

}}
"""


def gen_response_status(pkg):
    return f"""\
package {pkg}.response;
public enum ResponseStatus {{
    ELABORATO("ELABORATO"), IN_ELABORAZIONE("IN ELABORAZIONE"),
    IN_ERRORE("IN ERRORE"),  PRESO_IN_CARICO("PRESO IN CARICO");
    private final String status;
    ResponseStatus(String s) {{ this.status = s; }}
    public String getStatus() {{ return status; }}
}}
"""


def gen_mdc_filter(pkg):
    return f"""\
package {pkg}.filter;

import org.jboss.logging.MDC;
import {pkg}.utils.Constants;
import {pkg}.utils.Utility;
import jakarta.annotation.Priority;
import jakarta.inject.Inject;
import jakarta.ws.rs.Priorities;
import jakarta.ws.rs.container.*;
import jakarta.ws.rs.core.MultivaluedMap;
import jakarta.ws.rs.ext.Provider;

@Provider
@Priority(Priorities.AUTHENTICATION)
public class MdcHeadersFilter implements ContainerRequestFilter, ContainerResponseFilter {{

    public static final String PROP_KL           = "CTX_KL";
    public static final String PROP_TID          = "CTX_TID";
    public static final String PROP_MOD_ASYNC    = "CTX_MOD_ASYNC";
    public static final String PROP_PROCESS_TYPE = "CTX_PROCESS_TYPE";

    @Inject
    RequestHeadersContext requestHeadersContext;

    @Override
    public void filter(ContainerRequestContext req) {{
        requestHeadersContext.setStartNanos(System.nanoTime());
        requestHeadersContext.setPath("/" + req.getUriInfo().getPath());

        String kl  = Utility.defaultUuidIfBlank(req.getHeaderString(Constants.Headers.KEYLOGIC));
        String tid = Utility.defaultUuidIfBlank(req.getHeaderString(Constants.Headers.TRANSACTION_ID));
        boolean ma = Utility.parseBooleanOrDefault(req.getHeaderString(Constants.Headers.MOD_ASYNC), false);
        String pt  = Utility.defaultIfBlank(req.getHeaderString(Constants.Headers.PROCESS_TYPE), "N/A");

        MultivaluedMap<String, String> h = req.getHeaders();
        putIfBlank(h, Constants.Headers.KEYLOGIC,       kl);
        putIfBlank(h, Constants.Headers.TRANSACTION_ID, tid);
        putIfBlank(h, Constants.Headers.MOD_ASYNC,      String.valueOf(ma));
        putIfBlank(h, Constants.Headers.PROCESS_TYPE,   pt);

        req.setProperty(PROP_KL, kl); req.setProperty(PROP_TID, tid);
        req.setProperty(PROP_MOD_ASYNC, ma); req.setProperty(PROP_PROCESS_TYPE, pt);

        MDC.put(Constants.LogParams.KL,  kl);
        MDC.put(Constants.LogParams.TN,  tid);
        MDC.put(Constants.LogParams.PT,  pt);
        MDC.put(Constants.LogParams.MA,  String.valueOf(ma));
        MDC.put(Constants.LogParams.API, req.getMethod() + " /" + req.getUriInfo().getPath());

        requestHeadersContext.setKeyLogic(kl);
        requestHeadersContext.setTransactionId(tid);
        requestHeadersContext.setModAsync(ma);
        requestHeadersContext.setProcessType(pt);
    }}

    @Override
    public void filter(ContainerRequestContext req, ContainerResponseContext resp) {{
        try {{
            String kl  = (String) req.getProperty(PROP_KL);
            String tid = (String) req.getProperty(PROP_TID);
            Object maObj = req.getProperty(PROP_MOD_ASYNC);
            boolean ma = (maObj instanceof Boolean b) ? b : false;
            String pt  = (String) req.getProperty(PROP_PROCESS_TYPE);

            resp.getHeaders().putSingle(Constants.Headers.KEYLOGIC,       kl);
            resp.getHeaders().putSingle(Constants.Headers.TRANSACTION_ID, tid);
            resp.getHeaders().putSingle(Constants.Headers.MOD_ASYNC,      String.valueOf(ma));
            resp.getHeaders().putSingle(Constants.Headers.PROCESS_TYPE,   pt);
        }} finally {{ MDC.clear(); }}
    }}

    private static void putIfBlank(MultivaluedMap<String, String> h, String name, String value) {{
        String cur = h.getFirst(name);
        if (cur == null || cur.trim().isEmpty()) h.putSingle(name, value);
    }}
}}
"""


def gen_mdc_filter_dg(pkg):
    """DataGateway: senza RequestHeadersContext (classe Frontiera-only)."""
    return f"""\
package {pkg}.filter;

import org.jboss.logging.MDC;
import {pkg}.utils.Constants;
import {pkg}.utils.Utility;
import jakarta.annotation.Priority;
import jakarta.ws.rs.Priorities;
import jakarta.ws.rs.container.*;
import jakarta.ws.rs.core.MultivaluedMap;
import jakarta.ws.rs.ext.Provider;

@Provider
@Priority(Priorities.AUTHENTICATION)
public class MdcHeadersFilter implements ContainerRequestFilter, ContainerResponseFilter {{

    public static final String PROP_KL           = "CTX_KL";
    public static final String PROP_TID          = "CTX_TID";
    public static final String PROP_MOD_ASYNC    = "CTX_MOD_ASYNC";
    public static final String PROP_PROCESS_TYPE = "CTX_PROCESS_TYPE";

    @Override
    public void filter(ContainerRequestContext req) {{
        String kl  = Utility.defaultUuidIfBlank(req.getHeaderString(Constants.Headers.KEYLOGIC));
        String tid = Utility.defaultUuidIfBlank(req.getHeaderString(Constants.Headers.TRANSACTION_ID));
        boolean ma = Utility.parseBooleanOrDefault(req.getHeaderString(Constants.Headers.MOD_ASYNC), false);
        String pt  = Utility.defaultIfBlank(req.getHeaderString(Constants.Headers.PROCESS_TYPE), "N/A");

        MultivaluedMap<String, String> h = req.getHeaders();
        putIfBlank(h, Constants.Headers.KEYLOGIC,       kl);
        putIfBlank(h, Constants.Headers.TRANSACTION_ID, tid);
        putIfBlank(h, Constants.Headers.MOD_ASYNC,      String.valueOf(ma));
        putIfBlank(h, Constants.Headers.PROCESS_TYPE,   pt);

        req.setProperty(PROP_KL, kl); req.setProperty(PROP_TID, tid);
        req.setProperty(PROP_MOD_ASYNC, ma); req.setProperty(PROP_PROCESS_TYPE, pt);

        MDC.put(Constants.LogParams.KL,  kl);
        MDC.put(Constants.LogParams.TN,  tid);
        MDC.put(Constants.LogParams.PT,  pt);
        MDC.put(Constants.LogParams.MA,  String.valueOf(ma));
        MDC.put(Constants.LogParams.API, req.getMethod() + " /" + req.getUriInfo().getPath());
    }}

    @Override
    public void filter(ContainerRequestContext req, ContainerResponseContext resp) {{
        try {{
            String kl  = (String) req.getProperty(PROP_KL);
            String tid = (String) req.getProperty(PROP_TID);
            Object maObj = req.getProperty(PROP_MOD_ASYNC);
            boolean ma = (maObj instanceof Boolean b) ? b : false;
            String pt  = (String) req.getProperty(PROP_PROCESS_TYPE);

            resp.getHeaders().putSingle(Constants.Headers.KEYLOGIC,       kl);
            resp.getHeaders().putSingle(Constants.Headers.TRANSACTION_ID, tid);
            resp.getHeaders().putSingle(Constants.Headers.MOD_ASYNC,      String.valueOf(ma));
            resp.getHeaders().putSingle(Constants.Headers.PROCESS_TYPE,   pt);
        }} finally {{ MDC.clear(); }}
    }}

    private static void putIfBlank(MultivaluedMap<String, String> h, String name, String value) {{
        String cur = h.getFirst(name);
        if (cur == null || cur.trim().isEmpty()) h.putSingle(name, value);
    }}
}}
"""


def gen_global_openapi_filter(pkg):
    return f"""\
package {pkg}.filter;

import java.util.Map;

import org.eclipse.microprofile.openapi.OASFactory;
import org.eclipse.microprofile.openapi.OASFilter;
import org.eclipse.microprofile.openapi.models.OpenAPI;
import org.eclipse.microprofile.openapi.models.PathItem;
import org.eclipse.microprofile.openapi.models.media.Schema;
import org.eclipse.microprofile.openapi.models.parameters.Parameter;

import {pkg}.utils.Constants;

public class GlobalHeadersOpenApiFilter implements OASFilter {{

    @Override
    public void filterOpenAPI(OpenAPI openAPI) {{

        if (openAPI.getPaths() == null || openAPI.getPaths().getPathItems() == null) {{
            return;
        }}

        for (Map.Entry<String, PathItem> entry : openAPI.getPaths().getPathItems().entrySet()) {{
            addHeaders(entry.getValue());
        }}
    }}

    private void addHeaders(PathItem pathItem) {{
        addIfPresent(pathItem.getGET());
        addIfPresent(pathItem.getPOST());
        addIfPresent(pathItem.getPUT());
        addIfPresent(pathItem.getDELETE());
        addIfPresent(pathItem.getPATCH());
        addIfPresent(pathItem.getOPTIONS());
        addIfPresent(pathItem.getHEAD());
    }}

    private void addIfPresent(org.eclipse.microprofile.openapi.models.Operation operation) {{

        if (operation == null)
            return;

        operation.addParameter(header(Constants.Headers.KEYLOGIC, "Chiave di correlazione tecnica"));
        operation.addParameter(header(Constants.Headers.TRANSACTION_ID, "Transaction id tecnico"));
        operation.addParameter(header(Constants.Headers.MOD_ASYNC, "Modalità asincrona"));
        operation.addParameter(header(Constants.Headers.PROCESS_TYPE, "Tipo processo (GUI | FLUSSO | N/A)"));
    }}

    private Parameter header(String name, String description) {{

        Schema schema = OASFactory.createSchema();
        schema.setType(Schema.SchemaType.STRING);

        Parameter p = OASFactory.createParameter();
        p.setName(name);
        p.setIn(Parameter.In.HEADER);
        p.setRequired(false);
        p.setDescription(description);
        p.setSchema(schema);

        return p;
    }}
}}
"""


def gen_application_config(pkg):
    return f"""\
package {pkg}.config;

import java.time.LocalDateTime;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;

@ApplicationScoped
public class ApplicationConfig {{
    private static final Logger LOG = Logger.getLogger(ApplicationConfig.class);
    @ConfigProperty(name = "quarkus.application.name")    String appName;
    @ConfigProperty(name = "quarkus.application.version") String appVersion;

    void onStart(@Observes io.quarkus.runtime.StartupEvent ev) {{
        LOG.infof("════════════════════════════════════════");
        LOG.infof("  %s v%s started at %s", appName, appVersion, LocalDateTime.now());
        LOG.infof("════════════════════════════════════════");
    }}
    void onStop(@Observes io.quarkus.runtime.ShutdownEvent ev) {{
        LOG.infof("%s shutting down gracefully...", appName);
    }}
}}
"""


def gen_openapi_config(pkg, sn):
    title = " ".join(p.capitalize() for p in re.split(r"[-_]", sn)) + " API"
    return f"""\
package {pkg}.config;

import org.eclipse.microprofile.openapi.annotations.OpenAPIDefinition;
import org.eclipse.microprofile.openapi.annotations.enums.ParameterIn;
import org.eclipse.microprofile.openapi.annotations.enums.SecuritySchemeType;
import org.eclipse.microprofile.openapi.annotations.info.Info;
import org.eclipse.microprofile.openapi.annotations.parameters.Parameter;
import org.eclipse.microprofile.openapi.annotations.security.SecurityRequirement;
import org.eclipse.microprofile.openapi.annotations.security.SecurityScheme;
import org.eclipse.microprofile.openapi.annotations.servers.Server;

@OpenAPIDefinition(
    info = @Info(title = "{title}", version = "1.0"),
    servers = @Server(url = "/"),
    security = @SecurityRequirement(name = "bearerAuth"),
    components = @org.eclipse.microprofile.openapi.annotations.Components(parameters = {{
        @Parameter(name = "KEY-LOGIC",      in = ParameterIn.HEADER, description = "Chiave di correlazione tecnica",       required = false),
        @Parameter(name = "TRANSACTION-ID", in = ParameterIn.HEADER, description = "Transaction id tecnico",               required = false),
        @Parameter(name = "MOD-ASYNC",      in = ParameterIn.HEADER, description = "Modalità asincrona",                   required = false),
        @Parameter(name = "PROCESS-TYPE",   in = ParameterIn.HEADER, description = "Tipo processo (GUI | FLUSSO | N/A)",   required = false)
    }})
)
@SecurityScheme(
    securitySchemeName = "bearerAuth",
    type = SecuritySchemeType.HTTP,
    scheme = "bearer",
    bearerFormat = "JWT"
)
public class OpenApiConfig {{}}
"""


def gen_health_check(pkg):
    return f"""\
package {pkg}.health;

import org.eclipse.microprofile.health.*;
import org.jboss.logging.Logger;
import io.quarkus.redis.datasource.RedisDataSource;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class ApplicationHealthCheck {{
    private static final Logger LOG = Logger.getLogger(ApplicationHealthCheck.class);

    @Liveness
    HealthCheck liveness() {{ return () -> HealthCheckResponse.up("service-alive"); }}

    @Readiness
    @ApplicationScoped
    public static class RedisReadinessCheck implements HealthCheck {{
        @Inject RedisDataSource redis;
        @Override
        public HealthCheckResponse call() {{
            try {{ redis.execute("PING"); return HealthCheckResponse.up("redis-ready"); }}
            catch (Exception e) {{ LOG.error("Redis not ready", e); return HealthCheckResponse.down("redis-not-ready"); }}
        }}
    }}
}}
"""


def gen_topic_service(pkg):
    return f"""\
package {pkg}.service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import {pkg}.utils.Constants.Topic;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class TopicService {{
    private static final Logger logger = LoggerFactory.getLogger(TopicService.class);
    @ConfigProperty(name = "kafka-prefix.topics") String prefix;
    private final Map<String, String> realTopics = new ConcurrentHashMap<>();

    public String getRealTopic(String topicName) {{
        if (topicName == null || topicName.isBlank()) throw new IllegalArgumentException("Topic non valido");
        if (prefix == null || prefix.isBlank()) throw new IllegalStateException("'kafka-prefix.topics' non configurata");
        if (realTopics.isEmpty()) {{
            synchronized (this) {{
                if (realTopics.isEmpty()) {{
                    try {{ Topic.getAllTopicsValue().forEach(t -> realTopics.put(t, prefix + "-" + t)); }}
                    catch (Exception e) {{ logger.warn("Impossibile inizializzare cache topics", e); }}
                    logger.info("TopicService cache inizializzata. prefix={{}}", prefix);
                }}
            }}
        }}
        String real = realTopics.get(topicName);
        if (real == null) throw new IllegalArgumentException("Topic sconosciuto: " + topicName);
        return real;
    }}
}}
"""


def gen_kafka_producer(pkg, lib_pkg):
    """Frontiera: usa RequestHeadersContext per arricchire automaticamente gli header."""
    return f"""\
package {pkg}.kafka;

import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;

import org.apache.kafka.common.header.Headers;
import org.apache.kafka.common.header.internals.RecordHeaders;
import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;
import org.eclipse.microprofile.reactive.messaging.Message;
import org.jboss.logging.Logger;

import io.smallrye.reactive.messaging.kafka.api.OutgoingKafkaRecordMetadata;
import {pkg}.filter.RequestHeadersContext;
import {pkg}.service.TopicService;
import {lib_pkg}.util.JsonUtils;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class KafkaGenericProducer {{

    private static final Logger LOG = Logger.getLogger(KafkaGenericProducer.class);

    @Inject
    TopicService topicService;

    @Inject
    RequestHeadersContext headersCtx;

    @Inject
    @Channel("kafka-out")
    Emitter<String> emitter;

    // ======================================================
    // API pubblica — header letti automaticamente dal contesto
    // ======================================================

    public void sendEvent(String flow, String topic, Object payload) {{
        String messageKey = UUID.randomUUID().toString();
        sendInternal(flow, topic, messageKey, payload);
    }}

    public void sendSerialEvent(String flow, String topic, String messageKey, Object payload) {{
        if (messageKey == null || messageKey.isBlank()) {{
            messageKey = UUID.randomUUID().toString();
        }}
        sendInternal(flow, topic, messageKey, payload);
    }}

    // ======================================================
    // API pubblica — header forniti esplicitamente dal chiamante
    // ======================================================

    public void sendSerialEventWithHeaders(String transId, String keyLogic, String processType,
            String flow, String topic, String messageKey, Object payload) {{
        if (messageKey == null) {{
            messageKey = UUID.randomUUID().toString();
        }}
        send(topicService.getRealTopic(topic), messageKey,
                JsonUtils.writeAsJsonPrettyLogStringWithoutNull(payload),
                Map.of("TRANSACTION-ID", transId, "KEY-LOGIC", keyLogic,
                       "PROCESS-TYPE", processType, "FLOW", flow,
                       "MESSAGE-KEY", messageKey, "content-type", "application/json"));
    }}

    public void sendEventWithHeaders(String transId, String keyLogic, String processType,
            String flow, String topic, Object payload) {{
        String messageKey = UUID.randomUUID().toString();
        send(topicService.getRealTopic(topic), messageKey,
                JsonUtils.writeAsJsonPrettyLogStringWithoutNull(payload),
                Map.of("TRANSACTION-ID", transId, "KEY-LOGIC", keyLogic,
                       "PROCESS-TYPE", processType, "FLOW", flow,
                       "MESSAGE-KEY", messageKey, "content-type", "application/json"));
    }}

    // ======================================================
    // Internals
    // ======================================================

    private void sendInternal(String flow, String topic, String messageKey, Object payload) {{
        String transId      = safeOrGenerated(headersCtx != null ? headersCtx.getTransactionId() : null);
        String keyLogic     = safeOrGenerated(headersCtx != null ? headersCtx.getKeyLogic() : null);
        String processType  = safeOrDefault(headersCtx != null ? headersCtx.getProcessType() : null, "N/A");

        send(topicService.getRealTopic(topic),
             messageKey,
             JsonUtils.writeAsJsonPrettyLogStringWithoutNull(payload),
             headersMap(transId, keyLogic, processType, flow, messageKey));
    }}

    private Map<String, String> headersMap(String transId, String keyLogic, String processType,
                                           String flow, String messageKey) {{
        return Map.of(
            "TRANSACTION-ID", transId,
            "KEY-LOGIC",      keyLogic,
            "PROCESS-TYPE",   processType,
            "FLOW",           flow,
            "MESSAGE-KEY",    messageKey,
            "content-type",   "application/json"
        );
    }}

    private void send(String topic, String key, String payload, Map<String, String> headers) {{
        Headers kafkaHeaders = toKafkaHeaders(headers);
        OutgoingKafkaRecordMetadata<String> metadata =
            OutgoingKafkaRecordMetadata.<String>builder()
                .withTopic(topic)
                .withKey(key)
                .withHeaders(kafkaHeaders)
                .build();
        Message<String> message = Message.of(payload).addMetadata(metadata);
        LOG.debugf("Sending message to topic [%s] with key [%s]", topic, key);
        emitter.send(message);
    }}

    private Headers toKafkaHeaders(Map<String, String> headers) {{
        Headers kafkaHeaders = new RecordHeaders();
        if (headers != null) {{
            headers.forEach((k, v) -> {{
                if (v != null) {{
                    kafkaHeaders.add(k, v.getBytes(StandardCharsets.UTF_8));
                }}
            }});
        }}
        return kafkaHeaders;
    }}

    private String safeOrGenerated(String v) {{
        return (v == null || v.isBlank()) ? UUID.randomUUID().toString() : v;
    }}

    private String safeOrDefault(String v, String def) {{
        return (v == null || v.isBlank()) ? def : v;
    }}
}}
"""


def gen_kafka_producer_dg(pkg, lib_pkg):
    """DataGateway: senza RequestHeadersContext, usa Instance<JsonWebToken> per sicurezza JWT."""
    return f"""\
package {pkg}.kafka;

import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;

import org.apache.kafka.common.header.Headers;
import org.apache.kafka.common.header.internals.RecordHeaders;
import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;
import org.eclipse.microprofile.reactive.messaging.Message;
import org.jboss.logging.Logger;

import io.smallrye.reactive.messaging.kafka.api.OutgoingKafkaRecordMetadata;
import {pkg}.service.TopicService;
import {lib_pkg}.util.JsonUtils;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class KafkaGenericProducer {{

    private static final Logger LOG = Logger.getLogger(KafkaGenericProducer.class);

    @Inject
    TopicService topicService;

    @Inject
    @Channel("kafka-out")
    Emitter<String> emitter;

    // ======================================================
    // API pubblica — header generati automaticamente
    // ======================================================

    public void sendEvent(String flow, String topic, Object payload) {{
        String messageKey = UUID.randomUUID().toString();
        sendInternal(flow, topic, messageKey, payload);
    }}

    public void sendSerialEvent(String flow, String topic, String messageKey, Object payload) {{
        if (messageKey == null || messageKey.isBlank()) {{
            messageKey = UUID.randomUUID().toString();
        }}
        sendInternal(flow, topic, messageKey, payload);
    }}

    // ======================================================
    // API pubblica — header forniti esplicitamente dal chiamante
    // ======================================================

    public void sendSerialEventWithHeaders(String transId, String keyLogic, String processType,
            String flow, String topic, String messageKey, Object payload) {{
        if (messageKey == null) {{
            messageKey = UUID.randomUUID().toString();
        }}
        send(topicService.getRealTopic(topic), messageKey,
                JsonUtils.writeAsJsonPrettyLogStringWithoutNull(payload),
                Map.of("TRANSACTION-ID", transId, "KEY-LOGIC", keyLogic,
                       "PROCESS-TYPE", processType, "FLOW", flow,
                       "MESSAGE-KEY", messageKey, "content-type", "application/json"));
    }}

    public void sendEventWithHeaders(String transId, String keyLogic, String processType,
            String flow, String topic, Object payload) {{
        String messageKey = UUID.randomUUID().toString();
        send(topicService.getRealTopic(topic), messageKey,
                JsonUtils.writeAsJsonPrettyLogStringWithoutNull(payload),
                Map.of("TRANSACTION-ID", transId, "KEY-LOGIC", keyLogic,
                       "PROCESS-TYPE", processType, "FLOW", flow,
                       "MESSAGE-KEY", messageKey, "content-type", "application/json"));
    }}

    // ======================================================
    // Internals
    // ======================================================

    private void sendInternal(String flow, String topic, String messageKey, Object payload) {{
        String transId     = safeOrGenerated(null);
        String keyLogic    = safeOrGenerated(null);
        String processType = safeOrDefault(null, "N/A");

        send(topicService.getRealTopic(topic),
             messageKey,
             JsonUtils.writeAsJsonPrettyLogStringWithoutNull(payload),
             headersMap(transId, keyLogic, processType, flow, messageKey));
    }}

    private Map<String, String> headersMap(String transId, String keyLogic, String processType,
                                           String flow, String messageKey) {{
        return Map.of(
            "TRANSACTION-ID", transId,
            "KEY-LOGIC",      keyLogic,
            "PROCESS-TYPE",   processType,
            "FLOW",           flow,
            "MESSAGE-KEY",    messageKey,
            "content-type",   "application/json"
        );
    }}

    private void send(String topic, String key, String payload, Map<String, String> headers) {{
        Headers kafkaHeaders = toKafkaHeaders(headers);
        OutgoingKafkaRecordMetadata<String> metadata =
            OutgoingKafkaRecordMetadata.<String>builder()
                .withTopic(topic)
                .withKey(key)
                .withHeaders(kafkaHeaders)
                .build();
        Message<String> message = Message.of(payload).addMetadata(metadata);
        LOG.debugf("Sending message to topic [%s] with key [%s]", topic, key);
        emitter.send(message);
    }}

    private Headers toKafkaHeaders(Map<String, String> headers) {{
        Headers kafkaHeaders = new RecordHeaders();
        if (headers != null) {{
            headers.forEach((k, v) -> {{
                if (v != null) {{
                    kafkaHeaders.add(k, v.getBytes(StandardCharsets.UTF_8));
                }}
            }});
        }}
        return kafkaHeaders;
    }}

    private String safeOrGenerated(String v) {{
        return (v == null || v.isBlank()) ? UUID.randomUUID().toString() : v;
    }}

    private String safeOrDefault(String v, String def) {{
        return (v == null || v.isBlank()) ? def : v;
    }}
}}
"""


def gen_kafka_consumer(pkg):
    return f"""\
package {pkg}.kafka;

import org.jboss.logging.Logger;
import {pkg}.service.TopicService;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

/** Consumer Kafka generico. Aggiungere metodi @Incoming("kafka-in") per ogni topic. */
@ApplicationScoped
public class KafkaGenericConsumer {{
    private static final Logger LOG = Logger.getLogger(KafkaGenericConsumer.class);
    @Inject TopicService topicService;
    // Esempio:
    // @Incoming("kafka-in") @Blocking
    // public CompletionStage<Void> consume(Message<String> message) {{
    //     LOG.infof("Received: %s", message.getPayload());
    //     return message.ack();
    // }}
}}
"""


def gen_sample_dto(pkg):
    return f"""\
package {pkg}.dto;

import lombok.Data; import lombok.NoArgsConstructor; import lombok.AllArgsConstructor; import lombok.Builder;
import com.fasterxml.jackson.annotation.JsonInclude;
import org.eclipse.microprofile.openapi.annotations.media.Schema;

@Data @NoArgsConstructor @AllArgsConstructor @Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(name = "SampleDTO", description = "DTO di esempio - sostituire con il proprio modello")
public class SampleDTO {{
    @Schema(description = "Identificativo univoco") private Long id;
    @Schema(description = "Codice elemento")        private String code;
    @Schema(description = "Descrizione elemento")   private String description;
    @Schema(description = "Stato elemento")         private String status;
}}
"""


def gen_sample_client(pkg, sn):
    client_key = f"{sn}-dg-client"
    return f"""\
package {pkg}.client;

import org.eclipse.microprofile.rest.client.annotation.RegisterProvider;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;
import {pkg}.dto.SampleDTO;
import {pkg}.filter.RestClientHeadersFilter;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Produces(MediaType.APPLICATION_JSON)
@RegisterRestClient(configKey = "{client_key}")
@RegisterProvider(RestClientHeadersFilter.class)
public interface SampleDgClient {{

    @GET @Path("/sample")
    Response getAll();

    @GET @Path("/sample/{{id}}")
    Response getById(@PathParam("id") Long id);

    @POST @Path("/sample/save")
    Response save(SampleDTO dto);
}}
"""


def gen_sample_service(pkg, lib_pkg):
    return f"""\
package {pkg}.service;

import java.util.List;
import java.util.Optional;

import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.jboss.logging.Logger;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.smallrye.common.annotation.RunOnVirtualThread;
import {pkg}.client.SampleDgClient;
import {pkg}.dto.SampleDTO;
import {pkg}.exception.RemoteCallException;
import {pkg}.filter.RequestHeadersContext;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.core.Response;

@ApplicationScoped
@RunOnVirtualThread
public class SampleService {{

    private static final Logger LOG = Logger.getLogger(SampleService.class);

    private static final TypeReference<List<SampleDTO>> LIST_TYPE = new TypeReference<>() {{}};

    @Inject
    @RestClient
    SampleDgClient client;

    @Inject
    ObjectMapper objectMapper;

    // ✅ Context CDI: propaga KL/TID/PT nel logging e negli header client
    @Inject
    RequestHeadersContext headersCtx;

    // =========================
    // GET ALL
    // =========================

    public List<SampleDTO> getAll() {{
        try (Response resp = client.getAll()) {{
            return handleListResponse(resp, "GET /sample");
        }}
    }}

    // =========================
    // GET BY ID
    // =========================

    public Optional<SampleDTO> getById(Long id) {{
        try (Response resp = client.getById(id)) {{
            int status = resp.getStatus();

            if (status == Response.Status.NOT_FOUND.getStatusCode()) {{
                return Optional.empty();
            }}
            if (status == Response.Status.OK.getStatusCode()) {{
                return Optional.ofNullable(resp.readEntity(SampleDTO.class));
            }}
            if (status == Response.Status.BAD_REQUEST.getStatusCode()) {{
                throw new IllegalArgumentException("getById: richiesta non valida. " + safeReadBody(resp));
            }}

            throw remoteError("GET /sample/{{id}}", status, resp);
        }}
    }}

    // =========================
    // SAVE
    // =========================

    public SampleDTO save(SampleDTO dto) {{
        try (Response resp = client.save(dto)) {{
            int status = resp.getStatus();

            if (status == Response.Status.OK.getStatusCode()
                    || status == Response.Status.CREATED.getStatusCode()) {{
                return resp.readEntity(SampleDTO.class);
            }}
            if (status == Response.Status.BAD_REQUEST.getStatusCode()) {{
                throw new IllegalArgumentException("save: richiesta non valida. " + safeReadBody(resp));
            }}

            throw remoteError("POST /sample/save", status, resp);
        }}
    }}

    // =========================
    // Helpers
    // =========================

    private List<SampleDTO> handleListResponse(Response resp, String operation) {{
        int status = resp.getStatus();

        if (status == Response.Status.NO_CONTENT.getStatusCode()) {{
            return List.of();
        }}
        if (status == Response.Status.OK.getStatusCode()) {{
            return readList(resp.readEntity(String.class));
        }}
        if (status == Response.Status.BAD_REQUEST.getStatusCode()) {{
            throw new IllegalArgumentException(operation + ": richiesta non valida. " + safeReadBody(resp));
        }}

        throw remoteError(operation, status, resp);
    }}

    private List<SampleDTO> readList(String json) {{
        if (json == null || json.isBlank()) return List.of();
        try {{
            return objectMapper.readValue(json, LIST_TYPE);
        }} catch (Exception e) {{
            throw new RemoteCallException("Impossibile deserializzare lista SampleDTO", e);
        }}
    }}

    private String safeReadBody(Response resp) {{
        try {{
            return resp.hasEntity() ? resp.readEntity(String.class) : "";
        }} catch (Exception e) {{
            return "";
        }}
    }}

    private RemoteCallException remoteError(String operation, int status, Response resp) {{
        String body = safeReadBody(resp);
        LOG.errorf("%s fallita. KL=%s TID=%s PT=%s HTTP=%d body=%s",
                operation,
                headersCtx.getKeyLogic(),
                headersCtx.getTransactionId(),
                headersCtx.getProcessType(),
                status,
                body
        );
        return new RemoteCallException(
                operation + " errore HTTP " + status + (body.isBlank() ? "" : (" - " + body))
        );
    }}
}}
"""


def gen_sample_resource(pkg, sn, lib_pkg):
    prefix = re.sub(r"[-_]", "", sn[:3].lower())
    return f"""\
package {pkg}.resource;

import java.util.List;
import java.util.Optional;

import io.smallrye.common.annotation.RunOnVirtualThread;
import {pkg}.dto.SampleDTO;
import {pkg}.exception.RemoteCallException;
import {pkg}.service.SampleService;
import {pkg}.utils.Utility;
import {lib_pkg}.annotation.AuthzRead;
import {lib_pkg}.annotation.AuthzWrite;
import {lib_pkg}.annotation.LogPmr;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("/")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RunOnVirtualThread
@LogPmr
public class SampleResource {{

    @Inject
    SampleService service;

    @Inject
    Utility utility;

    @GET
    @AuthzRead
    @Path("/{prefix}_sample_getall")
    public Response getAll() {{
        try {{
            List<SampleDTO> list = service.getAll();
            return utility.okOrEmpty(list);
        }} catch (IllegalArgumentException e) {{
            return utility.badRequest(e.getMessage());
        }} catch (RemoteCallException e) {{
            return utility.badGateway(e);
        }}
    }}

    @GET
    @AuthzRead
    @Path("/{prefix}_sample_id/{{id}}")
    public Response getById(@PathParam("id") Long id) {{
        if (id == null || id <= 0) {{
            return utility.badRequest("Path param 'id' non valido");
        }}
        try {{
            Optional<SampleDTO> opt = service.getById(id);
            return utility.okOrNotFound(opt, "Nessun elemento trovato per id=" + id);
        }} catch (IllegalArgumentException e) {{
            return utility.badRequest(e.getMessage());
        }} catch (RemoteCallException e) {{
            return utility.badGateway(e);
        }}
    }}

    @POST
    @AuthzWrite
    @Path("/{prefix}_sample_save")
    public Response save(SampleDTO dto) {{
        if (dto == null) {{
            return utility.badRequest("Body mancante o non valido");
        }}
        try {{
            SampleDTO saved = service.save(dto);
            return utility.created(saved);
        }} catch (IllegalArgumentException e) {{
            return utility.badRequest(e.getMessage());
        }} catch (RemoteCallException e) {{
            return utility.badGateway(e);
        }}
    }}
}}
"""


def gen_no_security_test_profile(pkg):
    return f"""\
package {pkg}.test;
import io.quarkus.test.junit.QuarkusTestProfile;
import java.util.Map;
public class NoSecurityTestProfile implements QuarkusTestProfile {{
    @Override public Map<String, String> getConfigOverrides() {{
        return Map.of(
            "quarkus.oidc.enabled", "false",
            "quarkus.arc.validate", "false",
            "security.enabled", "false",
            "quarkus.http.auth.permission.public.paths", "/*",
            "quarkus.http.auth.permission.public.policy", "permit",
            "quarkus.kafka.devservices.enabled", "false",
            "quarkus.apicurio-registry.devservices.enabled", "false"
        );
    }}
}}
"""


def gen_sample_resource_test(pkg, sn):
    prefix = re.sub(r"[-_]", "", sn[:3].lower())
    return f"""\
package {pkg}.test.resource;

import io.quarkus.test.junit.QuarkusTest;
import io.quarkus.test.junit.TestProfile;
import io.restassured.RestAssured;
import org.junit.jupiter.api.Test;
import {pkg}.test.NoSecurityTestProfile;
import static org.hamcrest.Matchers.*;

@QuarkusTest
@TestProfile(NoSecurityTestProfile.class)
class SampleResourceTest {{
    @Test void testGetAll_shouldReturn200Or204() {{
        RestAssured.given()
            .header("keyLogic","test-kl").header("transactionId","test-tid").header("processType","TEST")
            .when().get("/{prefix}_sample_getall")
            .then().statusCode(anyOf(is(200),is(204)));
    }}
    @Test void testGetById_missingId_shouldReturn400() {{
        RestAssured.given()
            .header("keyLogic","test-kl").header("transactionId","test-tid")
            .when().get("/{prefix}_sample_getbyid")
            .then().statusCode(400);
    }}
}}
"""


def gen_svc_dockerfile(sn):
    return f"""\
FROM registry.access.redhat.com/ubi8/openjdk-21:1.18
ENV LANGUAGE='en_US:en'
COPY --chown=185 target/quarkus-app/lib/ /deployments/lib/
COPY --chown=185 target/quarkus-app/*.jar /deployments/
COPY --chown=185 target/quarkus-app/app/ /deployments/app/
COPY --chown=185 target/quarkus-app/quarkus/ /deployments/quarkus/
EXPOSE 8090
USER 185
ENV JAVA_OPTS_APPEND="-Dquarkus.http.host=0.0.0.0 -Djava.util.logging.manager=org.jboss.logmanager.LogManager"
ENV JAVA_APP_JAR="/deployments/quarkus-run.jar"
ENTRYPOINT [ "/opt/jboss/container/java/run/run-java.sh" ]
"""


# ═════════════════════════════════════════════════════════════════════════════
# GENERATORS — DATAGATEWAY SPECIFIC
# ═════════════════════════════════════════════════════════════════════════════

def gen_pom_dg(sn, pkg, lib_group, lib_artifact):
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">

    <modelVersion>4.0.0</modelVersion>

    <groupId>{pkg}</groupId>
    <artifactId>{sn}</artifactId>
    <version>1.0.0-SNAPSHOT</version>

    <properties>
        <java.version>21</java.version>
        <lombok.version>1.18.32</lombok.version>
        <compiler-plugin.version>3.13.0</compiler-plugin.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <maven-surefire-plugin.version>3.2.5</maven-surefire-plugin.version>
        <quarkus.platform.group-id>io.quarkus.platform</quarkus.platform.group-id>
        <quarkus.platform.artifact-id>quarkus-bom</quarkus.platform.artifact-id>
        <quarkus.platform.version>3.9.2</quarkus.platform.version>
        <mapstruct.version>1.6.3</mapstruct.version>
        <shedlock.version>5.13.0</shedlock.version>
        <sonar.sources>
            src/main/java/{pkg_to_path(pkg)}/resource,src/main/java/{pkg_to_path(pkg)}/service,src/main/java/{pkg_to_path(pkg)}/utils
        </sonar.sources>
        <sonar.tests>src/test</sonar.tests>
        <sonar.java.coveragePlugin>jacoco</sonar.java.coveragePlugin>
        <sonar.dynamicAnalysis>reuseReports</sonar.dynamicAnalysis>
        <sonar.language>java</sonar.language>
        <argLine/>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>${{quarkus.platform.group-id}}</groupId>
                <artifactId>${{quarkus.platform.artifact-id}}</artifactId>
                <version>${{quarkus.platform.version}}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <!-- Common Library -->
        <dependency>
            <groupId>{lib_group}</groupId>
            <artifactId>{lib_artifact}</artifactId>
            <version>1.0.0-SNAPSHOT</version>
        </dependency>
        <!-- REST -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-rest</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-rest-jackson</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-rest-client-jackson</artifactId></dependency>
        <!-- VALIDATION -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-hibernate-validator</artifactId></dependency>
        <!-- DATABASE -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-hibernate-orm-panache</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-jdbc-mssql</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-flyway</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-hibernate-envers</artifactId></dependency>
        <!-- SCHEDULER -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-scheduler</artifactId></dependency>
        <dependency>
            <groupId>net.javacrumbs.shedlock</groupId><artifactId>shedlock-core</artifactId>
            <version>${{shedlock.version}}</version>
        </dependency>
        <dependency>
            <groupId>net.javacrumbs.shedlock</groupId><artifactId>shedlock-provider-jdbc-template</artifactId>
            <version>${{shedlock.version}}</version>
        </dependency>
        <!-- KAFKA -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-messaging-kafka</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-smallrye-reactive-messaging-kafka</artifactId></dependency>
        <!-- REDIS -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-redis-client</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-cache</artifactId></dependency>
        <!-- SECURITY -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-oidc</artifactId></dependency>
        <!-- OBSERVABILITY -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-smallrye-health</artifactId></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-micrometer-registry-prometheus</artifactId></dependency>
        <!-- OPENAPI -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-smallrye-openapi</artifactId></dependency>
        <!-- MAPSTRUCT -->
        <dependency>
            <groupId>org.mapstruct</groupId><artifactId>mapstruct</artifactId>
            <version>${{mapstruct.version}}</version>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId><artifactId>lombok</artifactId>
            <version>${{lombok.version}}</version><scope>provided</scope>
        </dependency>
        <!-- FAULT TOLERANCE -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-smallrye-fault-tolerance</artifactId></dependency>
        <!-- TEST -->
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-junit5-mockito</artifactId><scope>test</scope></dependency>
        <dependency><groupId>io.rest-assured</groupId><artifactId>rest-assured</artifactId><scope>test</scope></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-jdbc-h2</artifactId><scope>test</scope></dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>io.quarkus</groupId><artifactId>quarkus-maven-plugin</artifactId>
                <version>${{quarkus.platform.version}}</version>
                <executions><execution><goals><goal>build</goal></goals></execution></executions>
            </plugin>
            <plugin>
                <artifactId>maven-compiler-plugin</artifactId><version>${{compiler-plugin.version}}</version>
                <configuration>
                    <release>${{java.version}}</release>
                    <annotationProcessorPaths>
                        <path><groupId>org.mapstruct</groupId><artifactId>mapstruct-processor</artifactId><version>${{mapstruct.version}}</version></path>
                        <path><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId><version>${{lombok.version}}</version></path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId><artifactId>maven-surefire-plugin</artifactId>
                <version>${{maven-surefire-plugin.version}}</version>
                <configuration>
                    <argLine>@{{argLine}} -Djava.util.logging.manager=org.jboss.logmanager.LogManager -XX:+EnableDynamicAgentLoading</argLine>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.jacoco</groupId><artifactId>jacoco-maven-plugin</artifactId><version>0.8.14</version>
                <executions>
                    <execution><id>prepare-agent</id><goals><goal>prepare-agent</goal></goals><phase>initialize</phase></execution>
                    <execution><id>report</id><goals><goal>report</goal></goals><phase>verify</phase></execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
"""


def gen_application_properties_dg(sn, pkg, lib_pkg):
    short = to_short(sn)
    return f"""\
############################################
# QUARKUS CORE
############################################
quarkus.application.name={sn}
#quarkus.http.root-path=${{kapp:prefix}}
quarkus.http.port=${{QUARKUS_PORT:8090}}
quarkus.package.output-name={sn}

############################################
# LOGGING - GLOBAL
############################################
quarkus.log.console.enable=true
quarkus.log.level=${{LOG_LEVEL_ROOT_CONSOLE:INFO}}
quarkus.log.category."io.quarkus.confluent".level=ERROR
quarkus.log.console.format=[%5p] %d{{yyyy-MM-dd HH:mm:ss.SSS}} API:%X{{API}} TRANS-ID:%X{{TN}} KEY-LOGIC:%X{{KL}} MESSAGE-KEY:%X{{MK}} PROCESS-TYPE:%X{{PT}} [%t] %c{{1}} - %s%e%n
quarkus.console.color=true

############################################
# CATEGORY LOGGERS
############################################
quarkus.log.category."{pkg}.service".level=${{LOG_LEVEL_SERVICE_CONSOLE:INFO}}
quarkus.log.category."{pkg}.resource".level=${{LOG_LEVEL_CONTROLLER_CONSOLE:INFO}}
quarkus.log.category."{lib_pkg}.interceptor".level=INFO

############################################
# DATASOURCE - SQL SERVER
############################################
quarkus.datasource.db-kind=mssql
quarkus.datasource.username=${{DB_USERNAME:sa}}
quarkus.datasource.password=${{DB_PASSWORD:Password1!}}
quarkus.datasource.jdbc.url=${{DB_URL:jdbc:sqlserver://localhost:1433;databaseName={short};encrypt=true;trustServerCertificate=true;loginTimeout=30}}

############################################
# HIBERNATE ORM / ENVERS
############################################
quarkus.hibernate-orm.database.generation=none
quarkus.hibernate-orm.log.sql=false

############################################
# FLYWAY
############################################
quarkus.flyway.enabled=false
quarkus.flyway.migrate-at-start=false
quarkus.flyway.baseline-on-migrate=false

############################################
# REDIS
############################################
quarkus.redis.hosts=${{REDIS_HOSTS:redis://localhost:6379}}

############################################
# APP CACHE
############################################
quarkus.cache.enabled=true
quarkus.cache.caffeine."{short}-sample".expire-after-write=10M

############################################
# KAFKA
############################################
kafka.bootstrap.servers=${{KAFKA_BOOTSTRAP_SERVERS:localhost:${{KAFKA_SERVER_PORT:9092}}}}
kafka-prefix.topics=${{KAFKA_TOPIC_PREFIX:prefix}}
kafka.security.protocol=SASL_SSL
kafka.sasl.mechanism=PLAIN
kafka.sasl.jaas.username=${{KAFKA_API_KEY:XXXXXXXXXX}}
kafka.sasl.jaas.password=${{KAFKA_API_SECRET:YYYYYYYYYY}}
kafka.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="${{kafka.sasl.jaas.username}}" password="${{kafka.sasl.jaas.password}}";
kafka.request.timeout.ms=30000
kafka.connections.max.idle.ms=540000
kafka.reconnect.backoff.ms=1000
kafka.reconnect.backoff.max.ms=10000
kafka.socket.keepalive.enable=true

############################################
# KAFKA PRODUCER
############################################
mp.messaging.outgoing.kafka-out.connector=smallrye-kafka
mp.messaging.outgoing.kafka-out.bootstrap.servers=${{kafka.bootstrap.servers}}
mp.messaging.outgoing.kafka-out.key.serializer=org.apache.kafka.common.serialization.StringSerializer
mp.messaging.outgoing.kafka-out.value.serializer=org.apache.kafka.common.serialization.StringSerializer
mp.messaging.outgoing.kafka-out.acks=all
mp.messaging.outgoing.kafka-out.retries=3

############################################
# KAFKA CONSUMER - sample-in
############################################
mp.messaging.incoming.sample-in.connector=smallrye-kafka
mp.messaging.incoming.sample-in.bootstrap.servers=${{kafka.bootstrap.servers}}
mp.messaging.incoming.sample-in.group.id=groupId-{sn}
mp.messaging.incoming.sample-in.auto.offset.reset=earliest
mp.messaging.incoming.sample-in.value.deserializer=org.apache.kafka.common.serialization.StringDeserializer
mp.messaging.incoming.sample-in.enable.auto.commit=false
mp.messaging.incoming.sample-in.max.poll.records=1
mp.messaging.incoming.sample-in.topic=${{kafka-prefix.topics}}-{short}-in

############################################
# SECURITY - OIDC
############################################
quarkus.oidc.auth-server-url=${{OIDC_AUTH_SERVER_URL:http://localhost:8080/realms/myrealm}}
quarkus.oidc.client-id=${{OIDC_CLIENT_ID:quarkus-client}}
quarkus.oidc.credentials.secret=${{OIDC_SECRET:mysecret}}

############################################
# OBSERVABILITY
############################################
quarkus.smallrye-health.root-path=/health
quarkus.micrometer.export.prometheus.path=/metrics

############################################
# OPENAPI
############################################
quarkus.swagger-ui.always-include=true
quarkus.swagger-ui.path=/swagger
quarkus.smallrye-openapi.path=/openapi
mp.openapi.filter={pkg}.filter.GlobalHeadersOpenApiFilter

############################################
# SCHEDULER
############################################
quarkus.scheduler.enabled=true
cron.clean.sample=0 0 5 * * ?

############################################
# DEV PROFILE
############################################
%dev.quarkus.hibernate-orm.enabled=true
%dev.quarkus.oidc.enabled=false
%dev.quarkus.http.auth.permission.public.paths=/*
%dev.quarkus.http.auth.permission.public.policy=permit
%dev.security.enabled=false
%dev.kafka.bootstrap.servers=localhost:${{KAFKA_SERVER_PORT:9092}}
%dev.kafka.security.protocol=PLAINTEXT
%dev.kafka.topics.auto-create=true
"""


def gen_application_test_properties_dg():
    return """\
# Database H2 in memoria per i test
quarkus.datasource.db-kind=h2
quarkus.datasource.jdbc.url=jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
quarkus.datasource.username=sa
quarkus.datasource.password=sa

quarkus.flyway.migrate-at-start=true
quarkus.security.enabled=false
quarkus.oidc.enabled=false
quarkus.kafka.devservices.enabled=false
quarkus.apicurio-registry.devservices.enabled=false

quarkus.log.level=INFO
quarkus.log.category."io.quarkus".level=DEBUG

quarkus.hibernate-orm.database.generation=drop-and-create
quarkus.hibernate-orm.log.sql=true

quarkus.http.test-port=0
quarkus.http.cors=false
"""


def gen_constants_dg(pkg, sn):
    short = to_short(sn)
    topic_in  = f"{short}-in"
    topic_out = f"{short}-out"
    topic_in_const  = f"{short.upper()}_IN_TOPIC"
    topic_out_const = f"{short.upper()}_OUT_TOPIC"
    return f"""\
package {pkg}.utils;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public interface Constants {{

    String TIMESTAMP_FORMAT = "yyyyMMddHHmmssSSS";
    String MSG_ERROR = "Error";

    interface Headers {{
        String TRANSACTION_ID = "transactionId";
        String KEYLOGIC       = "keyLogic";
        String MOD_ASYNC      = "modAsync";
        String PROCESS_TYPE   = "processType";
        String JWT            = "JWT";
        String AUTHORIZATION  = "Authorization";
        String FLOW           = "FLOW";
    }}

    interface LogParams {{
        String TN = "TN";
        String KL = "KL";
        String API = "API";
        String MK = "MK";
        String PT = "PT";
        String MA = "MA";
    }}

    interface MEDIATYPE {{
        String APP_JSON = "application/json";
    }}

    interface Topic {{
        String {topic_in_const}  = "{topic_in}";
        String {topic_out_const} = "{topic_out}";

        static List<String> getAllTopicsValue() throws IllegalArgumentException, IllegalAccessException {{
            List<Field> fields = Arrays.asList(Constants.Topic.class.getDeclaredFields());
            List<String> topics = new ArrayList<>();
            for (Field field : fields) {{
                Object object = field.get(null);
                if (object instanceof String) topics.add((String) object);
            }}
            return topics;
        }}
    }}
}}
"""


def gen_domain_entity(pkg, sn):
    cls = to_class_prefix(sn)
    table = cls.upper()
    return f"""\
package {pkg}.domain;

import java.time.LocalDateTime;

import org.hibernate.envers.Audited;
import org.hibernate.envers.NotAudited;

import io.quarkus.hibernate.orm.panache.PanacheEntityBase;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

@Entity
@Audited
@Table(name = "{table}")
public class {cls}Entity extends PanacheEntityBase {{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(nullable = false, updatable = false)
    private Long id;

    @NotBlank
    @Column(name = "CODE", nullable = false, length = 100)
    private String code;

    @Column(name = "DESCRIPTION", length = 250)
    private String description;

    @NotNull
    @Column(name = "STATUS", nullable = false)
    private Integer status;

    @Column(name = "ACTION_DATE", nullable = false)
    private LocalDateTime actionDate;

    @Column(name = "USER_ACTION", nullable = false, length = 50)
    private String userAction;

    @NotNull
    @Column(name = "IS_DELETED", nullable = false)
    private Integer isDeleted = 0;

    @NotAudited
    @Column(name = "NOTE", length = 4000)
    private String note;

    public Long getId() {{ return id; }}
    public void setId(Long id) {{ this.id = id; }}
    public String getCode() {{ return code; }}
    public void setCode(String code) {{ this.code = code; }}
    public String getDescription() {{ return description; }}
    public void setDescription(String description) {{ this.description = description; }}
    public Integer getStatus() {{ return status; }}
    public void setStatus(Integer status) {{ this.status = status; }}
    public LocalDateTime getActionDate() {{ return actionDate; }}
    public void setActionDate(LocalDateTime actionDate) {{ this.actionDate = actionDate; }}
    public String getUserAction() {{ return userAction; }}
    public void setUserAction(String userAction) {{ this.userAction = userAction; }}
    public Integer getIsDeleted() {{ return isDeleted; }}
    public void setIsDeleted(Integer isDeleted) {{ this.isDeleted = isDeleted; }}
    public String getNote() {{ return note; }}
    public void setNote(String note) {{ this.note = note; }}
}}
"""


def gen_revision_info(pkg):
    return f"""\
package {pkg}.domain;

import org.hibernate.envers.RevisionEntity;
import org.hibernate.envers.RevisionNumber;
import org.hibernate.envers.RevisionTimestamp;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "REVINFO", schema = "dbo")
@RevisionEntity
public class RevisionInfo {{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @RevisionNumber
    @Column(name = "REV", nullable = false)
    private Integer rev;

    @RevisionTimestamp
    @Column(name = "REVTSTMP")
    private Long revtstmp;

    public Integer getRev() {{ return rev; }}
    public Long getRevtstmp() {{ return revtstmp; }}
    public void setRev(Integer rev) {{ this.rev = rev; }}
    public void setRevtstmp(Long revtstmp) {{ this.revtstmp = revtstmp; }}
}}
"""


def gen_repository(pkg, sn):
    cls = to_class_prefix(sn)
    return f"""\
package {pkg}.repository;

import java.util.List;
import java.util.Optional;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import {pkg}.domain.{cls}Entity;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;
import jakarta.transaction.Transactional;

@ApplicationScoped
public class {cls}Repository implements PanacheRepository<{cls}Entity> {{

    @Inject
    EntityManager em;

    public Optional<{cls}Entity> findByCode(String code) {{
        return find("code = ?1 AND isDeleted = 0", code).firstResultOptional();
    }}

    public List<{cls}Entity> findAllActive() {{
        return list("isDeleted = 0");
    }}

    public List<{cls}Entity> findByStatus(Integer status) {{
        return list("status = ?1 AND isDeleted = 0", status);
    }}

    @Transactional
    @SuppressWarnings("unchecked")
    public List<{cls}Entity> findLastNoLock(int limit) {{
        return getEntityManager()
            .createNativeQuery("SELECT * FROM {cls.upper()} WITH (NOLOCK) WHERE IS_DELETED = 0 ORDER BY ACTION_DATE DESC", {cls}Entity.class)
            .setMaxResults(limit)
            .getResultList();
    }}
}}
"""


def gen_mapper(pkg, sn):
    cls = to_class_prefix(sn)
    return f"""\
package {pkg}.mapper;

import java.util.List;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingConstants;
import org.mapstruct.MappingTarget;

import {pkg}.domain.{cls}Entity;
import {pkg}.dto.{cls}DTO;

@Mapper(componentModel = MappingConstants.ComponentModel.JAKARTA)
public interface {cls}Mapper {{

    {cls}DTO toDto({cls}Entity entity);

    @Mapping(target = "id", ignore = true)
    {cls}Entity toEntity({cls}DTO dto);

    List<{cls}DTO> toDtoList(List<{cls}Entity> entities);

    @Mapping(target = "id", ignore = true)
    void updateEntityFromDto({cls}DTO dto, @MappingTarget {cls}Entity entity);
}}
"""


def gen_sample_dto_dg(pkg, sn):
    cls = to_class_prefix(sn)
    return f"""\
package {pkg}.dto;

import java.time.LocalDateTime;

import lombok.Builder;

@Builder
public record {cls}DTO(
    String code,
    String description,
    Integer status,
    LocalDateTime actionDate,
    String userAction,
    Integer isDeleted,
    String note
) {{}}
"""


def gen_utility_dg(pkg):
    return f"""\
package {pkg}.utils;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import {pkg}.exception.RemoteCallException;
import jakarta.ws.rs.core.Response;

public class Utility {{

    // =========================
    // Helpers statici puri
    // =========================

    public static String defaultUuidIfBlank(String v) {{
        return (v == null || v.isBlank()) ? UUID.randomUUID().toString() : v;
    }}

    public static boolean parseBooleanOrDefault(String v, boolean defaultValue) {{
        if (v == null || v.isBlank()) return defaultValue;
        String s = v.trim().toLowerCase();
        if ("true".equals(s)) return true;
        if ("false".equals(s)) return false;
        return defaultValue;
    }}

    public static String defaultIfBlank(String value, String defaultValue) {{
        return (value == null || value.trim().isEmpty()) ? defaultValue : value;
    }}

    public static long elapsedMs(long startNanos) {{
        return (System.nanoTime() - startNanos) / 1_000_000;
    }}

    public static String safe(Object v) {{
        if (v == null) return "null";
        String s = String.valueOf(v).trim();
        if (s.isEmpty()) return "blank";
        return (s.length() > 120) ? s.substring(0, 120) + "..." : s;
    }}

    // =========================
    // Common headers
    // =========================

    public static Response.ResponseBuilder withCommonHeaders(
            Response.ResponseBuilder rb,
            String keyLogic,
            String transactionId,
            boolean modAsync,
            String processType
    ) {{
        return rb
                .header(Constants.Headers.KEYLOGIC, keyLogic)
                .header(Constants.Headers.TRANSACTION_ID, transactionId)
                .header(Constants.Headers.MOD_ASYNC, String.valueOf(modAsync))
                .header(Constants.Headers.PROCESS_TYPE, processType);
    }}

    // =========================
    // Success responses
    // =========================

    public static <T> Response ok(
            T data,
            String path,
            String keyLogic,
            String transactionId,
            boolean modAsync,
            String processType,
            long startNanos
    ) {{
        return withCommonHeaders(
                Response.ok(data),
                keyLogic, transactionId, modAsync, processType
        ).build();
    }}

    public static <T> Response created(
            T data,
            String path,
            String keyLogic,
            String transactionId,
            boolean modAsync,
            String processType,
            long startNanos
    ) {{
        return withCommonHeaders(
                Response.status(Response.Status.CREATED).entity(data),
                keyLogic, transactionId, modAsync, processType
        ).build();
    }}

    public static <T> Response okOrEmpty(
            List<T> list,
            String path,
            String keyLogic,
            String transactionId,
            boolean modAsync,
            String processType,
            long startNanos
    ) {{
        if (list == null) list = List.of();
        return ok(list, path, keyLogic, transactionId, modAsync, processType, startNanos);
    }}

    public static <T> Response okOrNotFound(
            Optional<T> opt,
            String notFoundMessage,
            String path,
            String keyLogic,
            String transactionId,
            boolean modAsync,
            String processType,
            long startNanos
    ) {{
        if (opt == null || opt.isEmpty()) {{
            return notFound(notFoundMessage, path,
                    keyLogic, transactionId, modAsync, processType, startNanos);
        }}
        return ok(opt.get(), path, keyLogic, transactionId, modAsync, processType, startNanos);
    }}

    public static Response noContentOnlyHeaders(
            String keyLogic,
            String transactionId,
            boolean modAsync,
            String processType
    ) {{
        return withCommonHeaders(
                Response.noContent(),
                keyLogic, transactionId, modAsync, processType
        ).build();
    }}

    // =========================
    // Error responses
    // =========================

    public record ErrorPayload(
            String messageType,
            String messageCode,
            String messageDescription
    ) {{}}

    public static Response badRequest(
            String message,
            String path,
            String keyLogic,
            String transactionId,
            boolean modAsync,
            String processType,
            long startNanos
    ) {{
        return withCommonHeaders(
                Response.status(Response.Status.BAD_REQUEST)
                        .entity(new ErrorPayload("ERROR", "BAD_REQUEST", message)),
                keyLogic, transactionId, modAsync, processType
        ).build();
    }}

    public static Response notFound(
            String message,
            String path,
            String keyLogic,
            String transactionId,
            boolean modAsync,
            String processType,
            long startNanos
    ) {{
        return withCommonHeaders(
                Response.status(Response.Status.NOT_FOUND)
                        .entity(new ErrorPayload("ERROR", "NOT_FOUND", message)),
                keyLogic, transactionId, modAsync, processType
        ).build();
    }}

    public static Response badGateway(
            RemoteCallException e,
            String path,
            String keyLogic,
            String transactionId,
            boolean modAsync,
            String processType,
            long startNanos
    ) {{
        return withCommonHeaders(
                Response.status(Response.Status.BAD_GATEWAY)
                        .entity(new ErrorPayload("ERROR", "BAD_GATEWAY", e.getMessage())),
                keyLogic, transactionId, modAsync, processType
        ).build();
    }}
}}
"""


def gen_sample_service_dg(pkg, sn, lib_pkg):
    cls = to_class_prefix(sn)
    return f"""\
package {pkg}.service;

import java.util.List;
import java.util.Optional;

import org.eclipse.microprofile.jwt.JsonWebToken;
import org.jboss.logging.Logger;

import io.smallrye.common.annotation.RunOnVirtualThread;
import {pkg}.domain.{cls}Entity;
import {pkg}.dto.{cls}DTO;
import {pkg}.mapper.{cls}Mapper;
import {pkg}.repository.{cls}Repository;
import {lib_pkg}.util.JsonUtils;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Instance;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;

@ApplicationScoped
@RunOnVirtualThread
public class {cls}Service {{

    private static final Logger LOG = Logger.getLogger({cls}Service.class);

    @Inject
    {cls}Repository repository;

    @Inject
    {cls}Mapper mapper;

    @Inject
    Instance<JsonWebToken> jwt;

    public List<{cls}DTO> getAll() {{
        return mapper.toDtoList(repository.listAll());
    }}

    public {cls}DTO getById(Long id) {{
        {cls}Entity entity = repository.findById(id);
        return mapper.toDto(entity);
    }}

    public {cls}DTO getByCode(String code) {{
        return repository.findByCode(code)
                .map(mapper::toDto)
                .orElse(null);
    }}

    public List<{cls}DTO> getLastExecutions(int limit) {{
        return mapper.toDtoList(repository.findLastNoLock(limit));
    }}

    @Transactional
    public {cls}DTO save({cls}DTO dto) {{
        Optional<{cls}Entity> existing = repository.findByCode(dto.code());
        {cls}Entity entityToSave;
        if (existing.isPresent()) {{
            entityToSave = existing.get();
            mapper.updateEntityFromDto(dto, entityToSave);
        }} else {{
            entityToSave = mapper.toEntity(dto);
            repository.persist(entityToSave);
        }}
        return mapper.toDto(entityToSave);
    }}

    public void processSaveFromKafka(String payload) {{
        try {{
            {cls}DTO dto = JsonUtils.getObject(payload, {cls}DTO.class);
            save(dto);
        }} catch (Exception ex) {{
            LOG.error("Error processing Kafka message: " + ex.getMessage(), ex);
        }}
    }}

    protected String currentUser() {{
        try {{
            if (!jwt.isUnsatisfied() && !jwt.isAmbiguous()) {{
                JsonWebToken token = jwt.get();
                return token != null ? token.getName() : "system";
            }}
        }} catch (Exception ignored) {{}}
        return "system";
    }}
}}
"""


def gen_sample_resource_dg(pkg, sn, lib_pkg):
    cls = to_class_prefix(sn)
    short = to_short(sn)
    path_prefix = short[:12] if len(short) > 12 else short
    return f"""\
package {pkg}.resource;

import java.util.List;
import java.util.Optional;

import io.smallrye.common.annotation.RunOnVirtualThread;
import {pkg}.dto.{cls}DTO;
import {pkg}.service.{cls}Service;
import {pkg}.utils.RequestCtx;
import {pkg}.utils.Utility;
import {lib_pkg}.annotation.LogPmr;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("/{path_prefix}")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@RunOnVirtualThread
@LogPmr
public class {cls}Resource {{

    @Inject
    {cls}Service service;

    @Context
    ContainerRequestContext ctx;

    // ======================================================
    // GET ALL
    // ======================================================
    @GET
    public Response getAll() {{
        long start = System.nanoTime();
        final String path = "/{path_prefix}";

        String kl = RequestCtx.kl(ctx);
        String tid = RequestCtx.tid(ctx);
        boolean modAsync = RequestCtx.modAsync(ctx);
        String processType = RequestCtx.processType(ctx);

        List<{cls}DTO> list = service.getAll();

        return Utility.okOrEmpty(
                list, path, kl, tid, modAsync, processType, start
        );
    }}

    // ======================================================
    // GET BY ID
    // ======================================================
    @GET
    @Path("/{{id}}")
    public Response getById(@PathParam("id") Long id) {{
        long start = System.nanoTime();
        final String path = "/{path_prefix}/{{id}}";

        String kl = RequestCtx.kl(ctx);
        String tid = RequestCtx.tid(ctx);
        boolean modAsync = RequestCtx.modAsync(ctx);
        String processType = RequestCtx.processType(ctx);

        if (id == null || id <= 0) {{
            return Utility.badRequest(
                    "Path param 'id' non valido",
                    path, kl, tid, modAsync, processType, start
            );
        }}

        {cls}DTO dto = service.getById(id);

        return Utility.okOrNotFound(
                Optional.ofNullable(dto),
                "Nessun elemento trovato per id=" + id,
                path, kl, tid, modAsync, processType, start
        );
    }}

    // ======================================================
    // GET BY CODE
    // ======================================================
    @GET
    @Path("/code/{{code}}")
    public Response getByCode(@PathParam("code") String code) {{
        long start = System.nanoTime();
        final String path = "/{path_prefix}/code/{{code}}";

        String kl = RequestCtx.kl(ctx);
        String tid = RequestCtx.tid(ctx);
        boolean modAsync = RequestCtx.modAsync(ctx);
        String processType = RequestCtx.processType(ctx);

        if (code == null || code.isBlank()) {{
            return Utility.badRequest(
                    "Path param 'code' non valido",
                    path, kl, tid, modAsync, processType, start
            );
        }}

        {cls}DTO dto = service.getByCode(code);

        return Utility.okOrNotFound(
                Optional.ofNullable(dto),
                "Nessun elemento trovato per code=" + code,
                path, kl, tid, modAsync, processType, start
        );
    }}

    // ======================================================
    // GET LAST EXECUTIONS
    // ======================================================
    @GET
    @Path("/last-executions")
    public Response getLastExecutions(
            @QueryParam("limit") @DefaultValue("10") int limit) {{

        long start = System.nanoTime();
        final String path = "/{path_prefix}/last-executions";

        String kl = RequestCtx.kl(ctx);
        String tid = RequestCtx.tid(ctx);
        boolean modAsync = RequestCtx.modAsync(ctx);
        String processType = RequestCtx.processType(ctx);

        if (limit <= 0) {{
            return Utility.badRequest(
                    "Query param 'limit' deve essere > 0",
                    path, kl, tid, modAsync, processType, start
            );
        }}

        List<{cls}DTO> list = service.getLastExecutions(limit);

        return Utility.okOrEmpty(
                list, path, kl, tid, modAsync, processType, start
        );
    }}

    // ======================================================
    // SAVE
    // ======================================================
    @POST
    @Path("/save")
    public Response save({cls}DTO dto) {{
        long start = System.nanoTime();
        final String path = "/{path_prefix}/save";

        String kl = RequestCtx.kl(ctx);
        String tid = RequestCtx.tid(ctx);
        boolean modAsync = RequestCtx.modAsync(ctx);
        String processType = RequestCtx.processType(ctx);

        if (dto == null) {{
            return Utility.badRequest(
                    "Body mancante o non valido",
                    path, kl, tid, modAsync, processType, start
            );
        }}

        boolean exists = dto.code() != null
                && !dto.code().isBlank()
                && service.getByCode(dto.code()) != null;

        {cls}DTO saved = service.save(dto);

        return exists
                ? Utility.ok(saved, path, kl, tid, modAsync, processType, start)
                : Utility.created(saved, path, kl, tid, modAsync, processType, start);
    }}
}}
"""


def gen_kafka_consumer_dg(pkg, sn):
    cls = to_class_prefix(sn)
    short = to_short(sn)
    return f"""\
package {pkg}.kafka;

import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.CompletionStage;
import java.util.function.BiConsumer;

import org.apache.kafka.common.header.Header;
import org.apache.kafka.common.header.Headers;
import org.apache.kafka.common.header.internals.RecordHeaders;
import org.eclipse.microprofile.reactive.messaging.Acknowledgment;
import org.eclipse.microprofile.reactive.messaging.Incoming;
import org.eclipse.microprofile.reactive.messaging.Message;
import org.jboss.logging.Logger;
import org.jboss.logging.MDC;

import io.smallrye.common.annotation.Blocking;
import io.smallrye.reactive.messaging.kafka.api.IncomingKafkaRecordMetadata;
import {pkg}.service.{cls}Service;
import {pkg}.service.TopicService;
import {pkg}.utils.Constants;
import {pkg}.utils.Constants.Topic;
import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class KafkaGenericConsumer {{

    private static final Logger LOG = Logger.getLogger(KafkaGenericConsumer.class);

    @Inject
    TopicService topicService;

    @Inject
    {cls}Service {short}Service;

    private Map<String, BiConsumer<String, Headers>> handlers;

    @PostConstruct
    void init() {{
        handlers = Map.of(
            topicService.getRealTopic(Topic.{short.upper()}_IN_TOPIC), this::handleSampleIn
        );
        handlers.keySet().forEach(t -> LOG.infof("Kafka handler registered for topic: %s", t));
    }}

    @Incoming("sample-in")
    @Acknowledgment(Acknowledgment.Strategy.MANUAL)
    @Blocking
    public CompletionStage<Void> consumeSampleIn(Message<String> message) {{
        return consumeMessage(message);
    }}

    private CompletionStage<Void> consumeMessage(Message<String> message) {{
        try {{
            IncomingKafkaRecordMetadata<?, ?> metadata = message.getMetadata(IncomingKafkaRecordMetadata.class).orElse(null);
            String topic = metadata != null ? metadata.getTopic() : "unknown";
            Headers headers = metadata != null ? metadata.getHeaders() : new RecordHeaders();
            String payload = message.getPayload();
            MDC.put(Constants.LogParams.TN, extractHeader(headers, "TRANSACTION-ID"));
            MDC.put(Constants.LogParams.KL, extractHeader(headers, "KEY-LOGIC"));
            MDC.put(Constants.LogParams.PT, extractHeader(headers, "PROCESS-TYPE"));
            MDC.put(Constants.LogParams.MK, extractHeader(headers, "MESSAGE-KEY"));
            handlers.getOrDefault(topic, this::handleGeneric).accept(payload, headers);
            return message.ack();
        }} catch (Exception e) {{
            LOG.error("Error processing Kafka message", e);
            return message.ack();
        }} finally {{
            MDC.clear();
        }}
    }}

    private void handleSampleIn(String payload, Headers headers) {{
        LOG.infof("handleSampleIn: processing payload...");
        String flow = extractHeader(headers, "FLOW");
        if (flow != null && !flow.isBlank()) {{
            switch (flow) {{
                case "SAVE":
                    {short}Service.processSaveFromKafka(payload);
                    break;
                default:
                    LOG.warnf("Unknown flow '%s' in message headers, skipping", flow);
            }}
        }}
    }}

    private void handleGeneric(String payload, Headers headers) {{
        LOG.warn("No specific handler found for topic, using generic handler");
    }}

    private String extractHeader(Headers headers, String name) {{
        if (headers == null) return "";
        Header header = headers.lastHeader(name);
        return header != null ? new String(header.value(), StandardCharsets.UTF_8) : "";
    }}
}}
"""


def gen_dev_kafka_topic_initializer(pkg):
    return f"""\
package {pkg}.kafka;

import java.util.List;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;

import org.apache.kafka.clients.admin.AdminClient;
import org.apache.kafka.clients.admin.CreateTopicsResult;
import org.apache.kafka.clients.admin.NewTopic;
import org.apache.kafka.common.errors.TopicExistsException;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;

import {pkg}.service.TopicService;
import {pkg}.utils.Constants.Topic;

import io.quarkus.runtime.StartupEvent;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import jakarta.inject.Inject;

@ApplicationScoped
public class DevKafkaTopicInitializer {{

    private static final Logger LOG = Logger.getLogger(DevKafkaTopicInitializer.class);
    private static final long ADMIN_TIMEOUT_SECONDS = 10;

    @Inject
    TopicService topicService;

    @ConfigProperty(name = "kafka.bootstrap.servers")
    String bootstrapServers;

    @ConfigProperty(name = "kafka.topics.auto-create", defaultValue = "false")
    boolean autoCreateTopics;

    @ConfigProperty(name = "kafka.topics.partitions", defaultValue = "1")
    int partitions;

    @ConfigProperty(name = "kafka.topics.replication-factor", defaultValue = "1")
    short replicationFactor;

    void onStart(@Observes StartupEvent event) {{
        if (!autoCreateTopics) {{
            LOG.debug("Kafka DEV topic auto-creation disabled");
            return;
        }}
        LOG.info("DEV profile detected -> Kafka topic auto-creation enabled");

        List<String> topicsToEnsure;
        try {{
            topicsToEnsure = Topic.getAllTopicsValue().stream()
                    .filter(t -> t != null && !t.isBlank())
                    .map(topicService::getRealTopic)
                    .distinct()
                    .toList();
        }} catch (Exception e) {{
            LOG.error("Error reading Kafka topic constants from Constants.Topic", e);
            return;
        }}

        if (topicsToEnsure.isEmpty()) {{
            LOG.warn("No DEV Kafka topics to ensure (topic list is empty)");
            return;
        }}

        Properties props = new Properties();
        props.put("bootstrap.servers", bootstrapServers);

        try (AdminClient admin = AdminClient.create(props)) {{
            Set<String> existingTopics = admin.listTopics().names()
                    .get(ADMIN_TIMEOUT_SECONDS, TimeUnit.SECONDS);

            List<NewTopic> topicsToCreate = topicsToEnsure.stream()
                    .filter(t -> !existingTopics.contains(t))
                    .map(t -> new NewTopic(t, partitions, replicationFactor))
                    .toList();

            if (topicsToCreate.isEmpty()) {{
                LOG.info("All DEV Kafka topics already exist");
                return;
            }}

            CreateTopicsResult result = admin.createTopics(topicsToCreate);
            for (NewTopic nt : topicsToCreate) {{
                try {{
                    result.values().get(nt.name()).get(ADMIN_TIMEOUT_SECONDS, TimeUnit.SECONDS);
                    LOG.infof("Kafka DEV topic created: %s (partitions=%d, rf=%d)",
                            nt.name(), partitions, replicationFactor);
                }} catch (ExecutionException ee) {{
                    Throwable cause = ee.getCause();
                    if (cause instanceof TopicExistsException) {{
                        LOG.infof("Kafka DEV topic already exists (race ignored): %s", nt.name());
                    }} else {{
                        LOG.errorf(cause, "Error creating Kafka DEV topic: %s", nt.name());
                    }}
                }}
            }}
        }} catch (Exception e) {{
            LOG.error("Error while creating Kafka topics in DEV", e);
        }}
    }}
}}
"""


def gen_scheduled_job(pkg, sn):
    short = to_short(sn)
    return f"""\
package {pkg}.scheduler;

import java.time.Duration;
import java.time.Instant;

import org.jboss.logging.Logger;

import io.quarkus.scheduler.Scheduled;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import net.javacrumbs.shedlock.core.LockConfiguration;
import net.javacrumbs.shedlock.core.LockProvider;

@ApplicationScoped
public class ScheduledJob {{

    private static final Logger LOG = Logger.getLogger(ScheduledJob.class);

    @Inject
    LockProvider lockProvider;

    @Scheduled(cron = "${{cron.clean.sample}}")
    void cleanSample() {{
        LockConfiguration lock = new LockConfiguration(
                Instant.now(), "CLEAN_{short.upper()}",
                Duration.ofMinutes(30), Duration.ofMinutes(10));
        lockProvider.lock(lock).ifPresent(l -> {{
            try {{ executeClean(); }} finally {{ l.unlock(); }}
        }});
    }}

    private void executeClean() {{
        LOG.info("Esecuzione job schedulato per pulizia dati {sn}");
        // TODO: implementare la logica di pulizia
    }}
}}
"""


def gen_shedlock_config(pkg):
    return f"""\
package {pkg}.scheduler;

import javax.sql.DataSource;

import org.springframework.jdbc.core.JdbcTemplate;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;
import jakarta.inject.Inject;
import net.javacrumbs.shedlock.core.LockProvider;
import net.javacrumbs.shedlock.provider.jdbctemplate.JdbcTemplateLockProvider;

@ApplicationScoped
public class ShedLockConfig {{

    @Inject
    DataSource dataSource;

    @Produces
    @ApplicationScoped
    LockProvider lockProvider() {{
        return new JdbcTemplateLockProvider(
                JdbcTemplateLockProvider.Configuration.builder()
                        .withJdbcTemplate(new JdbcTemplate(dataSource))
                        .usingDbTime()
                        .build()
        );
    }}
}}
"""


def gen_flyway_migration(sn):
    cls = to_class_prefix(sn)
    table = cls.upper()
    return f"""\
CREATE TABLE [dbo].[{table}](
    [ID]          [bigint] IDENTITY(1,1) NOT NULL,
    [CODE]        [varchar](100) NOT NULL,
    [DESCRIPTION] [varchar](250) NULL,
    [STATUS]      [int] NOT NULL,
    [ACTION_DATE] [datetime] NOT NULL,
    [USER_ACTION] [varchar](50) NOT NULL,
    [IS_DELETED]  [int] NOT NULL DEFAULT 0,
    [NOTE]        [nvarchar](4000) NULL,
    CONSTRAINT [PK_{table}] PRIMARY KEY CLUSTERED ([ID] ASC),
    CONSTRAINT [UQ_{table}_CODE] UNIQUE NONCLUSTERED ([CODE] ASC)
);

CREATE TABLE [dbo].[{table}_AUD](
    [ID]          [bigint] NOT NULL,
    [REV]         [int] NOT NULL,
    [REVTYPE]     [tinyint] NOT NULL,
    [CODE]        [varchar](100) NOT NULL,
    [DESCRIPTION] [varchar](250) NULL,
    [STATUS]      [int] NOT NULL,
    [ACTION_DATE] [datetime] NOT NULL,
    [USER_ACTION] [varchar](50) NOT NULL,
    [IS_DELETED]  [int] NULL,
    CONSTRAINT [PK_{table}_AUD] PRIMARY KEY CLUSTERED ([ID] ASC, [REV] ASC),
    CONSTRAINT [FK_{table}_AUD_REVINFO] FOREIGN KEY([REV]) REFERENCES [dbo].[REVINFO] ([REV])
);

CREATE TABLE [dbo].[REVINFO](
    [REV]     [int] IDENTITY(1,1) NOT NULL,
    [REVTSTMP] [bigint] NULL,
    PRIMARY KEY CLUSTERED ([REV] ASC)
);

CREATE TABLE [dbo].[shedlock](
    [name]      [varchar](50) NOT NULL,
    [lock_until] [datetime] NULL,
    [locked_at]  [datetime] NULL,
    [locked_by]  [varchar](250) NOT NULL,
    CONSTRAINT [PK_shedlock] PRIMARY KEY CLUSTERED ([name] ASC)
);
"""


def gen_sample_resource_test_dg(pkg, sn):
    cls = to_class_prefix(sn)
    short = to_short(sn)
    path_prefix = short[:12] if len(short) > 12 else short
    return f"""\
package {pkg}.test.resource;

import io.quarkus.test.junit.QuarkusTest;
import io.quarkus.test.junit.TestProfile;
import io.restassured.RestAssured;
import org.junit.jupiter.api.Test;
import {pkg}.test.NoSecurityTestProfile;
import static org.hamcrest.Matchers.*;

@QuarkusTest
@TestProfile(NoSecurityTestProfile.class)
class {cls}ResourceTest {{

    @Test
    void testGetAll_shouldReturn200Or204() {{
        RestAssured.given()
            .header("keyLogic", "test-kl")
            .header("transactionId", "test-tid")
            .header("processType", "TEST")
            .when().get("/{path_prefix}")
            .then().statusCode(anyOf(is(200), is(204)));
    }}

    @Test
    void testGetById_invalidId_shouldReturn400() {{
        RestAssured.given()
            .header("keyLogic", "test-kl")
            .header("transactionId", "test-tid")
            .when().get("/{path_prefix}/0")
            .then().statusCode(400);
    }}

    @Test
    void testSave_nullBody_shouldReturn400() {{
        RestAssured.given()
            .header("keyLogic", "test-kl")
            .header("transactionId", "test-tid")
            .contentType("application/json")
            .when().post("/{path_prefix}/save")
            .then().statusCode(anyOf(is(400), is(415)));
    }}
}}
"""


# ═════════════════════════════════════════════════════════════════════════════
# GENERATORS — LIBRERIA COMUNE
# ═════════════════════════════════════════════════════════════════════════════

def gen_lib_pom(lib_name, lib_group, lib_pkg):
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">

    <modelVersion>4.0.0</modelVersion>

    <groupId>{lib_group}</groupId>
    <artifactId>{lib_name}</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <properties>
        <java.version>21</java.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <quarkus.platform.group-id>io.quarkus.platform</quarkus.platform.group-id>
        <quarkus.platform.artifact-id>quarkus-bom</quarkus.platform.artifact-id>
        <quarkus.platform.version>3.9.2</quarkus.platform.version>
        <compiler-plugin.version>3.13.0</compiler-plugin.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>${{quarkus.platform.group-id}}</groupId>
                <artifactId>${{quarkus.platform.artifact-id}}</artifactId>
                <version>${{quarkus.platform.version}}</version>
                <type>pom</type><scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-rest</artifactId><scope>provided</scope></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-rest-client-jackson</artifactId><scope>provided</scope></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-oidc</artifactId><scope>provided</scope></dependency>
        <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-redis-client</artifactId><scope>provided</scope></dependency>
        <dependency><groupId>org.apache.httpcomponents</groupId><artifactId>httpclient</artifactId><version>4.5.14</version></dependency>
        <dependency><groupId>com.fasterxml.jackson.core</groupId><artifactId>jackson-databind</artifactId></dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>${{compiler-plugin.version}}</version>
                <configuration><release>${{java.version}}</release></configuration>
            </plugin>
        </plugins>
    </build>
</project>
"""


def gen_lib_application_properties():
    return """\
############################################
# AUTHORIZATION REST CLIENT
############################################
authorization-client/mp-rest/url=${AUTHZ_URL:http://localhost:8090/authorization}
authorization-client/mp-rest/connectTimeout=2000
authorization-client/mp-rest/readTimeout=3000

############################################
# ADFS TOKEN (CLIENT CREDENTIALS M2M)
############################################
adsf.token.url=${ADSF_TOKEN_URL:https://your-adfs/token}
adsf.client.id=${ADSF_CLIENT_ID:your-client-id}
adsf.client.secret=${ADSF_CLIENT_SECRET:your-secret}
# Resource audience ADFS (App ID URI del backend target)
adsf.resource.prefix=${ADSF_RESOURCE_PREFIX:your-prefix}
# Scope default
adsf.scope.default=${ADSF_SCOPE:default}

############################################
# REDIS (cache distribuita)
############################################
quarkus.redis.hosts=${REDIS_HOSTS:redis://localhost:6379}

############################################
# APP CACHE (Redis - custom)
############################################
app.cache.redis.prefix=${CACHE_REDIS_PREFIX:cache}
# TTL cache getWithBody di AdsfRestClientService (secondi)
cache.adsf-rest-client.get-with-body.ttl-seconds=${CACHE_ADSF_GET_WITH_BODY_TTL:300}

############################################
# B2B TOKEN (HMAC-SHA256)
############################################
security.b2b.secret=${B2B_SECRET:a3f8c2d91e4b7065f2a8c3d4e5f6071829a3b4c5d6e7f8091a2b3c4d5e6f7a8}
security.b2b.token-ttl-seconds=${B2B_TOKEN_TTL:300}
security.enabled=${SECURITY_ENABLED:true}
security.authz.bypass=${SECURITY_AUTHZ_BYPASS:false}
"""


def gen_lib_application_test_properties():
    return """\
quarkus.security.enabled=false
quarkus.oidc.enabled=false
quarkus.kafka.devservices.enabled=false
quarkus.log.level=INFO
quarkus.http.test-port=0
"""


def gen_lib_beans_xml():
    return """\
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="https://jakarta.ee/xml/ns/jakartaee"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee
                           https://jakarta.ee/xml/ns/jakartaee/beans_4_0.xsd"
       bean-discovery-mode="annotated">
</beans>
"""


def gen_lib_authz_read(lib_pkg):
    return f"""\
package {lib_pkg}.annotation;

import jakarta.ws.rs.NameBinding;
import java.lang.annotation.*;

@NameBinding
@Retention(RetentionPolicy.RUNTIME)
@Target({{ElementType.TYPE, ElementType.METHOD}})
public @interface AuthzRead {{}}
"""


def gen_lib_authz_write(lib_pkg):
    return f"""\
package {lib_pkg}.annotation;

import jakarta.ws.rs.NameBinding;
import java.lang.annotation.*;

@NameBinding
@Retention(RetentionPolicy.RUNTIME)
@Target({{ElementType.TYPE, ElementType.METHOD}})
public @interface AuthzWrite {{}}
"""


def gen_lib_log_pmr(lib_pkg):
    return f"""\
package {lib_pkg}.annotation;

import jakarta.interceptor.InterceptorBinding;
import java.lang.annotation.*;

@InterceptorBinding
@Target({{ElementType.METHOD, ElementType.TYPE}})
@Retention(RetentionPolicy.RUNTIME)
public @interface LogPmr {{}}
"""


def gen_lib_authz_request(lib_pkg):
    return f"""\
package {lib_pkg}.request;

import java.util.Set;

public record AuthzRequest(
        String userId,
        String context,
        String permit,
        Set<String> roles
) {{}}
"""


def gen_lib_authz_response(lib_pkg):
    return f"""\
package {lib_pkg}.response;

public record AuthzResponse(boolean enabled, String reason) {{}}
"""


def gen_lib_authorization_client(lib_pkg):
    return f"""\
package {lib_pkg}.client;

import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;
import {lib_pkg}.request.AuthzRequest;
import {lib_pkg}.response.AuthzResponse;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;

@Path("/authorization")
@RegisterRestClient(configKey = "authorization-client")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public interface AuthorizationClient {{
    @POST @Path("/check-authorization")
    AuthzResponse check(
            @HeaderParam("Authorization") String bearer,
            AuthzRequest request
    );
}}
"""


def gen_lib_authz_service(lib_pkg):
    return f"""\
package {lib_pkg}.service;

import com.auth0.jwt.interfaces.DecodedJWT;
import {lib_pkg}.client.AuthorizationClient;
import {lib_pkg}.filter.B2BTokenFilter;
import {lib_pkg}.request.AuthzRequest;
import {lib_pkg}.response.AuthzResponse;
import {lib_pkg}.util.AuthorizationUtils;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.ForbiddenException;
import jakarta.ws.rs.NotAuthorizedException;
import jakarta.ws.rs.ServiceUnavailableException;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.core.Context;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.jboss.logging.Logger;
import java.util.Set;

@ApplicationScoped
public class AuthzService {{

    private static final Logger LOG = Logger.getLogger(AuthzService.class);

    public enum Permit {{ READ, WRITE }}

    @Context
    ContainerRequestContext req;

    @Inject
    @RestClient
    AuthorizationClient authorizationClient;

    @ConfigProperty(name = "security.authz.bypass", defaultValue = "false")
    boolean authzBypass;

    public void assertAuthorized(String context, Permit permit) {{

        // bypass B2B
        if (Boolean.TRUE.equals(req.getProperty(B2BTokenFilter.B2B_SUPER_USER_KEY))) {{
            LOG.infof("B2B SUPER_USER bypass. context=%s permit=%s", context, permit.name());
            return;
        }}

        // bypass dev/test
        if (authzBypass) {{
            LOG.infof("AuthzBypass attivo -> skip authorization check. context=%s permit=%s", context, permit.name());
            return;
        }}

        String bearer = AuthorizationUtils.getBearer(req);
        DecodedJWT jwt = AuthorizationUtils.decode(bearer);
        String userId = AuthorizationUtils.resolveUserId(jwt);
        Set<String> roles = AuthorizationUtils.resolveRoles(jwt);

        try {{
            AuthzRequest authzReq = new AuthzRequest(userId, context, permit.name(), roles);
            AuthzResponse resp = authorizationClient.check(bearer, authzReq);
            if (resp == null || !resp.enabled()) {{
                String reason = (resp != null && resp.reason() != null && !resp.reason().isBlank())
                        ? resp.reason() : "User not enabled";
                throw new ForbiddenException(reason);
            }}
        }} catch (ForbiddenException | NotAuthorizedException e) {{
            throw e;
        }} catch (Exception e) {{
            throw new ServiceUnavailableException("Authorization service unavailable");
        }}
    }}
}}
"""


def gen_lib_authz_read_filter(lib_pkg):
    return f"""\
package {lib_pkg}.filter;

import {lib_pkg}.annotation.AuthzRead;
import {lib_pkg}.resolver.MinimalContextResolver;
import {lib_pkg}.service.AuthzService;
import jakarta.annotation.Priority;
import jakarta.inject.Inject;
import jakarta.inject.Singleton;
import jakarta.ws.rs.Priorities;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerRequestFilter;
import jakarta.ws.rs.container.ResourceInfo;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.ext.Provider;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;

@Provider
@AuthzRead
@Singleton
@Priority(Priorities.AUTHORIZATION)
public class AuthzReadFilter implements ContainerRequestFilter {{

    private static final Logger LOG = Logger.getLogger(AuthzReadFilter.class);

    @Context
    ResourceInfo resourceInfo;

    @Inject
    AuthzService authzService;

    @ConfigProperty(name = "security.enabled", defaultValue = "true")
    boolean securityEnabled;

    @Override
    public void filter(ContainerRequestContext req) {{

        LOG.infof("AuthzReadFilter HIT — method=%s path=%s auth=%s",
                req.getMethod(),
                req.getUriInfo().getRequestUri(),
                req.getHeaderString("Authorization") != null ? "PRESENT" : "MISSING");

        if (!securityEnabled) {{
            LOG.debug("Security disabled -> skip AuthzReadFilter");
            return;
        }}

        if (resourceInfo == null || resourceInfo.getResourceMethod() == null) {{
            LOG.warn("ResourceInfo not available -> skip AuthzReadFilter");
            return;
        }}

        boolean enabledForMethod = resourceInfo.getResourceMethod()
                .isAnnotationPresent(AuthzRead.class);

        if (!enabledForMethod) {{
            return;
        }}

        String context = MinimalContextResolver.build(
                resourceInfo.getResourceClass(),
                resourceInfo.getResourceMethod()
        );

        if (context == null || context.isBlank()) {{
            LOG.warn("Context blank -> skip AuthzReadFilter");
            return;
        }}

        LOG.debugf("AuthzReadFilter invoked -> %s#%s context=%s",
                resourceInfo.getResourceClass().getSimpleName(),
                resourceInfo.getResourceMethod().getName(),
                context
        );

        authzService.assertAuthorized(context, AuthzService.Permit.READ);
    }}
}}
"""


def gen_lib_authz_write_filter(lib_pkg):
    return f"""\
package {lib_pkg}.filter;

import {lib_pkg}.annotation.AuthzWrite;
import {lib_pkg}.resolver.MinimalContextResolver;
import {lib_pkg}.service.AuthzService;
import jakarta.annotation.Priority;
import jakarta.inject.Inject;
import jakarta.inject.Singleton;
import jakarta.ws.rs.Priorities;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerRequestFilter;
import jakarta.ws.rs.container.ResourceInfo;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.ext.Provider;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;

@Provider
@AuthzWrite
@Singleton
@Priority(Priorities.AUTHORIZATION)
public class AuthzWriteFilter implements ContainerRequestFilter {{

    private static final Logger LOG = Logger.getLogger(AuthzWriteFilter.class);

    @Context
    ResourceInfo resourceInfo;

    @Inject
    AuthzService authzService;

    @ConfigProperty(name = "security.enabled", defaultValue = "true")
    boolean securityEnabled;

    @Override
    public void filter(ContainerRequestContext req) {{

        if (!securityEnabled) {{
            LOG.debug("Security disabled -> skip AuthzWriteFilter");
            return;
        }}

        if (resourceInfo == null || resourceInfo.getResourceMethod() == null) {{
            LOG.warn("ResourceInfo not available -> skip AuthzWriteFilter");
            return;
        }}

        boolean enabledForMethod = resourceInfo.getResourceMethod()
                .isAnnotationPresent(AuthzWrite.class);

        if (!enabledForMethod) {{
            return;
        }}

        String context = MinimalContextResolver.build(
                resourceInfo.getResourceClass(),
                resourceInfo.getResourceMethod()
        );

        if (context == null || context.isBlank()) {{
            LOG.warn("Context blank -> skip AuthzWriteFilter");
            return;
        }}

        LOG.debugf("AuthzWriteFilter invoked -> %s#%s context=%s",
                resourceInfo.getResourceClass().getSimpleName(),
                resourceInfo.getResourceMethod().getName(),
                context
        );

        authzService.assertAuthorized(context, AuthzService.Permit.WRITE);
    }}
}}
"""


def gen_lib_log_pmr_interceptor(lib_pkg):
    return f"""\
package {lib_pkg}.interceptor;

import org.jboss.logging.Logger;
import {lib_pkg}.annotation.LogPmr;
import jakarta.annotation.Priority;
import jakarta.interceptor.AroundInvoke;
import jakarta.interceptor.Interceptor;
import jakarta.interceptor.InvocationContext;

@LogPmr @Interceptor @Priority(Interceptor.Priority.APPLICATION)
public class LogPmrInterceptor {{
    private static final Logger LOG = Logger.getLogger(LogPmrInterceptor.class);

    @AroundInvoke
    public Object logMethodEntryExit(InvocationContext ctx) throws Exception {{
        String m = ctx.getMethod().getName();
        LOG.infof("IN %s", m);
        long start = System.nanoTime();
        try {{ return ctx.proceed(); }}
        finally {{ LOG.infof("OUT %s elapsedMs=%d", m, (System.nanoTime()-start)/1_000_000); }}
    }}
}}
"""


def gen_lib_minimal_context_resolver(lib_pkg):
    return f"""\
package {lib_pkg}.resolver;

import jakarta.ws.rs.Path;
import java.lang.reflect.Method;

public final class MinimalContextResolver {{
    private MinimalContextResolver() {{}}

    public static String build(Class<?> resourceClass, Method resourceMethod) {{
        String cp = extractPath(resourceClass.getAnnotation(Path.class));
        String mp = extractPath(resourceMethod != null ? resourceMethod.getAnnotation(Path.class) : null);
        return normalize(join(cp, mp));
    }}
    public static String buildStrict(Class<?> resourceClass, Method resourceMethod) {{
        if (resourceClass.getAnnotation(Path.class) == null)
            throw new IllegalStateException("Missing @Path on: " + resourceClass.getName());
        return build(resourceClass, resourceMethod);
    }}
    private static String extractPath(Path p) {{ return p == null ? "" : p.value(); }}
    private static String join(String a, String b) {{
        a = trimSlashes(a); b = trimSlashes(b);
        if (a.isEmpty() && b.isEmpty()) return "/";
        if (a.isEmpty()) return "/" + b;
        if (b.isEmpty()) return "/" + a;
        return "/" + a + "/" + b;
    }}
    private static String trimSlashes(String s) {{
        if (s == null) return "";
        s = s.trim();
        while (s.startsWith("/")) s = s.substring(1);
        while (s.endsWith("/"))   s = s.substring(0, s.length()-1);
        return s;
    }}
    private static String normalize(String raw) {{
        if (raw == null || raw.trim().isEmpty()) return "/";
        String s = raw.trim();
        if (!s.startsWith("/")) s = "/" + s;
        while (s.length() > 1 && s.endsWith("/")) s = s.substring(0, s.length()-1);
        while (s.contains("//")) s = s.replace("//", "/");
        return s;
    }}
}}
"""


def gen_lib_jwt_user_id_resolver(lib_pkg):
    return f"""\
package {lib_pkg}.resolver;

import com.auth0.jwt.JWT;
import com.auth0.jwt.interfaces.DecodedJWT;
import java.util.List;

public final class JwtUserIdResolver {{

    private JwtUserIdResolver() {{}}

    public static String resolve(String bearer) {{

        if (bearer == null || bearer.isBlank()) {{
            return null;
        }}

        DecodedJWT jwt = decode(bearer);

        if (notBlank(jwt.getSubject())) {{
            return jwt.getSubject();
        }}

        for (String claim : List.of("userId", "user_id", "preferred_username", "username")) {{
            String value = jwt.getClaim(claim).asString();
            if (notBlank(value)) {{
                return value;
            }}
        }}

        String name = jwt.getClaim("name").asString();
        if (notBlank(name)) {{
            return name;
        }}

        return null;
    }}

    private static DecodedJWT decode(String bearer) {{
        return JWT.decode(stripBearer(bearer));
    }}

    private static String stripBearer(String bearer) {{
        return bearer.startsWith("Bearer ") ? bearer.substring(7) : bearer;
    }}

    private static boolean notBlank(String s) {{
        return s != null && !s.trim().isEmpty();
    }}
}}
"""


def gen_lib_jwt_roles_resolver(lib_pkg):
    return f"""\
package {lib_pkg}.resolver;

import com.auth0.jwt.JWT;
import com.auth0.jwt.interfaces.DecodedJWT;
import java.util.*;

public final class JwtRolesResolver {{

    private JwtRolesResolver() {{}}

    public static Set<String> resolveAllRoles(String bearer) {{

        if (bearer == null || bearer.isBlank()) {{
            return Collections.emptySet();
        }}

        DecodedJWT jwt = decode(bearer);
        Set<String> roles = new HashSet<>();

        List<String> rolesList = jwt.getClaim("roles").asList(String.class);
        if (rolesList != null) {{
            roles.addAll(rolesList);
        }}

        String role = jwt.getClaim("role").asString();
        if (role != null && !role.isBlank()) {{
            roles.add(role);
        }}

        return roles;
    }}

    private static DecodedJWT decode(String bearer) {{
        return JWT.decode(stripBearer(bearer));
    }}

    private static String stripBearer(String bearer) {{
        return bearer.startsWith("Bearer ") ? bearer.substring(7) : bearer;
    }}
}}
"""


# ═════════════════════════════════════════════════════════════════════════════
# SCAFFOLD FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def gen_lib_authorization_utils(lib_pkg):
    return f"""\
package {lib_pkg}.util;

import com.auth0.jwt.JWT;
import com.auth0.jwt.interfaces.DecodedJWT;
import jakarta.ws.rs.NotAuthorizedException;
import jakarta.ws.rs.container.ContainerRequestContext;
import java.util.*;

public final class AuthorizationUtils {{

    private AuthorizationUtils() {{}}

    // =========================================================
    // BEARER HEADER
    // =========================================================
    public static String getBearer(ContainerRequestContext req) {{
        String header = req.getHeaderString("Authorization");
        if (header == null || header.isBlank()) {{
            throw new NotAuthorizedException("Missing Authorization header");
        }}
        return header;
    }}

    public static String extractToken(String bearer) {{
        return bearer.startsWith("Bearer ") ? bearer.substring(7) : bearer;
    }}

    // =========================================================
    // JWT PARSING (senza validazione firma — la firma è verificata dall'authorization service)
    // =========================================================
    public static DecodedJWT decode(String bearer) {{
        return JWT.decode(extractToken(bearer));
    }}

    // =========================================================
    // USER ID
    // =========================================================
    public static String resolveUserId(DecodedJWT jwt) {{
        for (String claim : List.of("userID", "user_id", "preferred_username", "username")) {{
            String value = jwt.getClaim(claim).asString();
            if (notBlank(value)) return value;
        }}
        String name = jwt.getClaim("name").asString();
        if (notBlank(name)) return name;
        return null;
    }}

    // =========================================================
    // ROLES
    // =========================================================
    public static Set<String> resolveRoles(DecodedJWT jwt) {{
        Set<String> roles = new HashSet<>();
        List<String> list = jwt.getClaim("roles").asList(String.class);
        if (list != null) roles.addAll(list);
        String role = jwt.getClaim("role").asString();
        if (notBlank(role)) roles.add(role);
        return roles;
    }}

    // =========================================================
    private static boolean notBlank(String s) {{
        return s != null && !s.trim().isEmpty();
    }}
}}
"""


def gen_lib_adsf_token_dto(lib_pkg):
    return f"""\
package {lib_pkg}.dto;

public record AdsfTokenDto(
    String access_token,
    String token_type,
    int expires_in,
    String scope
) {{}}
"""


def gen_lib_adsf_token_cache(lib_pkg):
    return f"""\
package {lib_pkg}.cache;

import java.util.Optional;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class AdsfTokenCache {{

    private String token;
    private long expiryEpochMillis;

    public synchronized Optional<String> getValidToken() {{
        if (token == null) return Optional.empty();
        long now = System.currentTimeMillis();
        if (now < (expiryEpochMillis - 10000)) return Optional.of(token);
        return Optional.empty();
    }}

    public synchronized void store(String token, int expiresInSeconds) {{
        this.token = token;
        this.expiryEpochMillis = System.currentTimeMillis() + (expiresInSeconds * 1000L);
    }}

    public synchronized void clear() {{
        this.token = null;
        this.expiryEpochMillis = 0;
    }}
}}
"""


def gen_lib_adsf_token_service(lib_pkg):
    return f"""\
package {lib_pkg}.service;

import {lib_pkg}.cache.AdsfTokenCache;
import {lib_pkg}.dto.AdsfTokenDto;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.client.Client;
import jakarta.ws.rs.client.ClientBuilder;
import jakarta.ws.rs.client.Entity;
import jakarta.ws.rs.core.Form;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@ApplicationScoped
public class AdsfTokenService {{

    private static final Logger LOG = LoggerFactory.getLogger(AdsfTokenService.class);

    @ConfigProperty(name = "adsf.token.url")
    String tokenUrl;

    @ConfigProperty(name = "adsf.client.id")
    String clientId;

    @ConfigProperty(name = "adsf.client.secret")
    String clientSecret;

    @ConfigProperty(name = "adsf.resource.prefix")
    String resourcePrefix;

    @ConfigProperty(name = "adsf.scope.default")
    String scope;

    @Inject
    AdsfTokenCache cache;

    private final Client client = ClientBuilder.newClient();

    /** Restituisce un token M2M valido (usa cache se presente). */
    public String getToken() {{
        return cache.getValidToken()
                .orElseGet(this::fetchAndCacheToken);
    }}

    public void invalidate() {{
        LOG.warn("Token ADFS invalidato");
        cache.clear();
    }}

    private String fetchAndCacheToken() {{
        LOG.debug("Recupero nuovo token ADFS per client_id={{}}", clientId);
        Form form = new Form()
                .param("grant_type", "client_credentials")
                .param("client_id", clientId)
                .param("client_secret", clientSecret)
                .param("resource", resourcePrefix)
                .param("scope", scope);

        try (Response response = client.target(tokenUrl)
                .request(MediaType.APPLICATION_JSON)
                .post(Entity.entity(form, MediaType.APPLICATION_FORM_URLENCODED))) {{

            int status = response.getStatus();
            if (status != Response.Status.OK.getStatusCode()) {{
                String body = response.readEntity(String.class);
                LOG.error("Errore ADFS token. HTTP={{}} body={{}}", status, body);
                throw new RuntimeException("Errore recupero token ADFS: HTTP " + status);
            }}

            AdsfTokenDto dto = response.readEntity(AdsfTokenDto.class);
            if (dto == null || dto.access_token() == null) {{
                throw new RuntimeException("Token ADFS nullo o malformato");
            }}
            cache.store(dto.access_token(), dto.expires_in());
            LOG.debug("Token cache-ato con expires_in={{}}", dto.expires_in());
            return dto.access_token();
        }}
    }}
}}
"""


def gen_lib_adsf_m2m_headers_factory(lib_pkg):
    return f"""\
package {lib_pkg}.factory;

import {lib_pkg}.service.AdsfTokenService;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.core.MultivaluedHashMap;
import jakarta.ws.rs.core.MultivaluedMap;
import org.eclipse.microprofile.rest.client.ext.ClientHeadersFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.List;

/**
 * Factory MicroProfile che inietta l'header Authorization Bearer M2M (ADFS)
 * su ogni chiamata del DataPlatformClient, senza usare un ClientRequestFilter.
 */
@ApplicationScoped
public class AdsfM2MHeadersFactory implements ClientHeadersFactory {{

    private static final Logger LOG = LoggerFactory.getLogger(AdsfM2MHeadersFactory.class);

    @Inject
    AdsfTokenService tokenService;

    @Override
    public MultivaluedMap<String, String> update(
            MultivaluedMap<String, String> incomingHeaders,
            MultivaluedMap<String, String> clientOutgoingHeaders) {{

        MultivaluedMap<String, String> headers = new MultivaluedHashMap<>();
        try {{
            headers.put("Authorization", List.of("Bearer " + tokenService.getToken()));
        }} catch (Exception ex) {{
            LOG.error("Errore generazione token ADFS per header M2M", ex);
            throw new RuntimeException("Errore generazione token M2M", ex);
        }}
        return headers;
    }}
}}
"""


def gen_lib_data_platform_client(lib_pkg):
    return f"""\
package {lib_pkg}.client;

import {lib_pkg}.factory.AdsfM2MHeadersFactory;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.rest.client.annotation.RegisterClientHeaders;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

/**
 * Client REST generico per DataPlatform.
 * AdsfM2MHeadersFactory inietta automaticamente il Bearer ADFS M2M.
 * Configurare: dataplatform-client/mp-rest/url
 */
@RegisterRestClient(configKey = "dataplatform-client")
@RegisterClientHeaders(AdsfM2MHeadersFactory.class)
@Path("/")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public interface DataPlatformClient {{

    @GET  @Path("/{{resource}}") Response get( @PathParam("resource") String resource);
    @POST @Path("/{{resource}}") Response post(@PathParam("resource") String resource, Object body);
}}
"""


def gen_lib_custom_http_client(lib_pkg):
    return f"""\
package {lib_pkg}.config;

import jakarta.enterprise.context.ApplicationScoped;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpEntityEnclosingRequestBase;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;
import java.net.URI;

/** Wrapper Apache HttpClient per GET con body (non supportato da JAX-RS standard). */
@ApplicationScoped
public class CustomHttpClient {{

    private final CloseableHttpClient client = HttpClients.createDefault();

    public record HttpResult(int statusCode, String body) {{}}

    public HttpResult getWithBody(String url, String body, String bearerToken) throws Exception {{
        HttpEntityEnclosingRequestBase request = new HttpEntityEnclosingRequestBase() {{
            @Override public String getMethod() {{ return "GET"; }}
        }};
        request.setURI(new URI(url));
        request.setHeader("Authorization", bearerToken);
        request.setHeader("Content-Type", "application/json");
        if (body != null) request.setEntity(new StringEntity(body, ContentType.APPLICATION_JSON));

        try (CloseableHttpResponse response = client.execute(request)) {{
            int statusCode = response.getStatusLine().getStatusCode();
            String responseBody = response.getEntity() != null
                    ? EntityUtils.toString(response.getEntity()) : null;
            return new HttpResult(statusCode, responseBody);
        }}
    }}
}}
"""


def gen_lib_cache_utils(lib_pkg):
    return f"""\
package {lib_pkg}.util;

import java.util.Objects;
import java.util.function.Supplier;

import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.quarkus.redis.datasource.RedisDataSource;
import io.quarkus.redis.datasource.value.ValueCommands;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

/** Utility Redis distribuita per cache-aside. Condivisa da tutti i microservizi PMR. */
@ApplicationScoped
public class CacheUtils {{

    private static final Logger LOG = LoggerFactory.getLogger(CacheUtils.class);

    private final ObjectMapper objectMapper;
    private final ValueCommands<String, String> values;

    @ConfigProperty(name = "app.cache.redis.prefix", defaultValue = "cache")
    String prefix;

    @Inject
    public CacheUtils(RedisDataSource redisDS, ObjectMapper objectMapper) {{
        this.objectMapper = objectMapper;
        this.values = redisDS.value(String.class);
    }}

    public String key(String domain, String feature, String... parts) {{
        StringBuilder sb = new StringBuilder(prefix)
                .append(":").append(sanitize(domain))
                .append(":").append(sanitize(feature));
        if (parts != null) {{
            for (String p : parts) {{
                if (p != null && !p.isBlank()) sb.append(":").append(sanitize(p));
            }}
        }}
        return sb.toString();
    }}

    private String sanitize(String s) {{
        return s.trim().replace(" ", "_");
    }}

    public <T> T get(String key, TypeReference<T> typeRef) {{
        Objects.requireNonNull(key, "key");
        Objects.requireNonNull(typeRef, "typeRef");
        try {{
            String json = values.get(key);
            if (json == null || json.isBlank()) return null;
            return objectMapper.readValue(json, typeRef);
        }} catch (Exception e) {{
            LOG.debug("Cache GET fallita (key={{}}): {{}}", key, e.toString());
            return null;
        }}
    }}

    public <T> void put(String key, T value, int ttlSeconds) {{
        Objects.requireNonNull(key, "key");
        if (ttlSeconds <= 0) {{
            LOG.debug("Cache PUT skipped (ttlSeconds<=0) key={{}}", key);
            return;
        }}
        try {{
            String json = objectMapper.writeValueAsString(value);
            values.setex(key, (long) ttlSeconds, json);
        }} catch (Exception e) {{
            LOG.debug("Cache PUT fallita (key={{}}): {{}}", key, e.toString());
        }}
    }}

    public <T> T getOrCompute(String key, TypeReference<T> typeRef, int ttlSeconds, Supplier<T> supplier) {{
        T cached = get(key, typeRef);
        if (cached != null) return cached;
        T computed = supplier.get();
        put(key, computed, ttlSeconds);
        return computed;
    }}
}}
"""


def gen_lib_adsf_rest_client_service(lib_pkg):
    return f"""\
package {lib_pkg}.service;

import {lib_pkg}.client.DataPlatformClient;
import {lib_pkg}.config.CustomHttpClient;
import {lib_pkg}.util.CacheUtils;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.jboss.resteasy.reactive.ClientWebApplicationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Servizio generico per chiamate a DataPlatform con autenticazione ADFS M2M.
 * getWithBody usa cache Redis distribuita. Gestisce retry (MAX 3) e token refresh su 401.
 */
@ApplicationScoped
public class AdsfRestClientService {{

    private static final Logger LOG = LoggerFactory.getLogger(AdsfRestClientService.class);
    private static final int MAX_RETRY = 3;
    private static final long RETRY_SLEEP_MS = 3000L;

    private static final TypeReference<CustomHttpClient.HttpResult> HTTP_RESULT_TYPE =
            new TypeReference<>() {{}};

    @Inject AdsfTokenService tokenService;
    @Inject @RestClient DataPlatformClient client;
    @Inject CustomHttpClient customHttpClient;
    @Inject ObjectMapper objectMapper;
    @Inject CacheUtils cacheUtils;

    @ConfigProperty(
        name = "cache.adsf-rest-client.get-with-body.ttl-seconds",
        defaultValue = "300"
    )
    int getWithBodyTtlSeconds;

    /** GET con body (Apache HttpClient) con cache Redis distribuita. */
    public CustomHttpClient.HttpResult getWithBody(
            String baseUrl, String resourcePath, Object requestBodyObj) throws Exception {{

        final String url = buildUrl(baseUrl, resourcePath);
        final String jsonBody = (requestBodyObj != null)
                ? objectMapper.writeValueAsString(requestBodyObj) : null;

        String cacheKey = cacheUtils.key(
                "adsf-rest-client", "get-with-body",
                "url=" + url,
                "body=" + (jsonBody != null ? String.valueOf(jsonBody.hashCode()) : "null")
        );

        CustomHttpClient.HttpResult cached = cacheUtils.get(cacheKey, HTTP_RESULT_TYPE);
        if (cached != null) {{
            LOG.debug("Cache HIT GET-with-body: {{}}", url);
            return cached;
        }}

        int attempt = 0;
        while (true) {{
            attempt++;
            try {{
                String token = tokenService.getToken();
                CustomHttpClient.HttpResult res = customHttpClient.getWithBody(url, jsonBody, "Bearer " + token);
                if (res.statusCode() == 401) {{
                    LOG.warn("GET-with-body: 401 su {{}} -> invalido token", url);
                    tokenService.invalidate();
                    throw new RetryableAuthException("401 from DataPlatform");
                }}
                if (res.statusCode() >= 200 && res.statusCode() < 300) {{
                    cacheUtils.put(cacheKey, res, getWithBodyTtlSeconds);
                    LOG.debug("Cache PUT GET-with-body: {{}} ttl={{}}s", url, getWithBodyTtlSeconds);
                }}
                return res;
            }} catch (RetryableAuthException ex) {{
                // retry
            }} catch (Exception ex) {{
                if (attempt > MAX_RETRY) throw new RuntimeException("Errore GET-with-body verso " + url, ex);
                LOG.error("Retry {{}}/{{}}: {{}}", attempt, MAX_RETRY, ex.getMessage());
            }}
            sleep();
        }}
    }}

    /** GET standard (MicroProfile REST Client). */
    public Response get(String resourcePath) throws Exception {{
        int attempt = 0;
        while (true) {{
            attempt++;
            try {{
                return client.get(resourcePath);
            }} catch (ClientWebApplicationException e) {{
                int status = getStatus(e);
                if (status == 401) tokenService.invalidate();
                if (attempt > MAX_RETRY) throw new RuntimeException("Errore GET HTTP " + status + " su " + resourcePath, e);
                LOG.error("Retry {{}}/{{}}: HTTP {{}}", attempt, MAX_RETRY, status);
            }} catch (Exception ex) {{
                if (attempt > MAX_RETRY) throw new RuntimeException("Errore GET su " + resourcePath, ex);
                LOG.error("Retry {{}}/{{}}: {{}}", attempt, MAX_RETRY, ex.getMessage());
            }}
            sleep();
        }}
    }}

    /** POST standard (MicroProfile REST Client). */
    public Response post(String resourcePath, Object request) throws Exception {{
        int attempt = 0;
        while (true) {{
            attempt++;
            try {{
                return client.post(resourcePath, request);
            }} catch (ClientWebApplicationException e) {{
                int status = getStatus(e);
                if (status == 401) tokenService.invalidate();
                if (attempt > MAX_RETRY) throw new RuntimeException("Errore POST HTTP " + status + " su " + resourcePath, e);
                LOG.error("Retry {{}}/{{}}: HTTP {{}}", attempt, MAX_RETRY, status);
            }} catch (Exception ex) {{
                if (attempt > MAX_RETRY) throw new RuntimeException("Errore POST su " + resourcePath, ex);
                LOG.error("Retry {{}}/{{}}: {{}}", attempt, MAX_RETRY, ex.getMessage());
            }}
            sleep();
        }}
    }}

    private String buildUrl(String baseUrl, String resourcePath) {{
        if (baseUrl == null) return resourcePath;
        if (baseUrl.endsWith("/") && resourcePath.startsWith("/"))
            return baseUrl.substring(0, baseUrl.length() - 1) + resourcePath;
        if (!baseUrl.endsWith("/") && !resourcePath.startsWith("/"))
            return baseUrl + "/" + resourcePath;
        return baseUrl + resourcePath;
    }}

    private static int getStatus(ClientWebApplicationException e) {{
        return (e.getResponse() != null) ? e.getResponse().getStatus() : -1;
    }}

    private void sleep() {{
        try {{ Thread.sleep(RETRY_SLEEP_MS); }}
        catch (InterruptedException e) {{ Thread.currentThread().interrupt(); throw new RuntimeException("Thread interrotto durante retry", e); }}
    }}

    private static class RetryableAuthException extends RuntimeException {{
        RetryableAuthException(String m) {{ super(m); }}
    }}
}}
"""


def gen_lib_b2b_token_utils(lib_pkg):
    return f"""\
package {lib_pkg}.util;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Base64;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;

import jakarta.enterprise.context.ApplicationScoped;

/**
 * Utility per generare e validare token B2B firmati con HMAC-SHA256.
 *
 * Formato token (Base64url):
 *   &lt;timestamp_epoch_seconds&gt;.&lt;signature_hmac_sha256&gt;
 *
 * Utilizzo lato client:
 *   String token = b2bTokenUtils.generateSuperUserToken();
 *   // → passa "Bearer &lt;token&gt;" nell'header Authorization della chiamata REST
 */
@ApplicationScoped
public class B2BTokenUtils {{

    private static final Logger LOG = Logger.getLogger(B2BTokenUtils.class);
    private static final String HMAC_ALGO = "HmacSHA256";

    @ConfigProperty(name = "security.b2b.secret")
    String secret;

    @ConfigProperty(name = "security.b2b.token-ttl-seconds", defaultValue = "300")
    long ttlSeconds;

    // ─────────────────────────────────────────────────────────────────────────
    // GENERA
    // ─────────────────────────────────────────────────────────────────────────

    /** Genera un token B2B valido per {{@code ttlSeconds}} secondi. */
    public String generateToken() {{
        long expiresAt = Instant.now().getEpochSecond() + ttlSeconds;
        String payload = String.valueOf(expiresAt);
        String signature = sign(payload);
        String token = Base64.getUrlEncoder().withoutPadding()
                .encodeToString((payload + "." + signature).getBytes(StandardCharsets.UTF_8));
        LOG.infof("Token B2B generato, scade alle epoch=%d (+%ds)", expiresAt, ttlSeconds);
        return token;
    }}

    /** Restituisce il valore completo dell'header Authorization: "Bearer &lt;token&gt;" */
    public String generateSuperUserToken() {{
        return "Bearer " + generateToken();
    }}

    // ─────────────────────────────────────────────────────────────────────────
    // VALIDA
    // ─────────────────────────────────────────────────────────────────────────

    /** Valida un token B2B ricevuto. @return true se valido e non scaduto */
    public boolean isValid(String token) {{
        try {{
            String decoded = new String(
                    Base64.getUrlDecoder().decode(token), StandardCharsets.UTF_8);
            String[] parts = decoded.split("\\\\.", 2);
            if (parts.length != 2) return false;

            long expiresAt = Long.parseLong(parts[0]);
            if (Instant.now().getEpochSecond() > expiresAt) {{
                LOG.warnf("Token B2B scaduto alle epoch=%d", expiresAt);
                return false;
            }}
            return constantTimeEquals(sign(parts[0]), parts[1]);
        }} catch (Exception e) {{
            LOG.warnf("Token B2B non valido: %s", e.getMessage());
            return false;
        }}
    }}

    // ─────────────────────────────────────────────────────────────────────────
    // PRIVATI
    // ─────────────────────────────────────────────────────────────────────────

    private String sign(String payload) {{
        try {{
            Mac mac = Mac.getInstance(HMAC_ALGO);
            mac.init(new SecretKeySpec(
                    secret.getBytes(StandardCharsets.UTF_8), HMAC_ALGO));
            byte[] raw = mac.doFinal(payload.getBytes(StandardCharsets.UTF_8));
            return Base64.getUrlEncoder().withoutPadding().encodeToString(raw);
        }} catch (Exception e) {{
            throw new IllegalStateException("Errore firma token B2B", e);
        }}
    }}

    /** Confronto in tempo costante per prevenire timing attack */
    private boolean constantTimeEquals(String a, String b) {{
        if (a.length() != b.length()) return false;
        int result = 0;
        for (int i = 0; i < a.length(); i++) result |= a.charAt(i) ^ b.charAt(i);
        return result == 0;
    }}
}}
"""


def gen_lib_b2b_token_filter(lib_pkg):
    return f"""\
package {lib_pkg}.filter;

import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;

import {lib_pkg}.util.B2BTokenUtils;
import jakarta.annotation.Priority;
import jakarta.inject.Inject;
import jakarta.ws.rs.Priorities;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerRequestFilter;
import jakarta.ws.rs.ext.Provider;

/**
 * Filtro JAX-RS che riconosce i token B2B firmati con HMAC-SHA256.
 *
 * Se il token nell'header Authorization è un B2B valido, imposta la proprietà
 * {{@code b2b.super_user = true}} nel contesto della richiesta: i filtri
 * AuthzReadFilter / AuthzWriteFilter possono usarla per fare bypass
 * dell'autorizzazione OIDC standard.
 *
 * Attivo solo quando {{@code security.enabled=true}} (default).
 */
@Provider
@Priority(Priorities.AUTHENTICATION - 10)
public class B2BTokenFilter implements ContainerRequestFilter {{

    private static final Logger LOG = Logger.getLogger(B2BTokenFilter.class);
    public static final String B2B_SUPER_USER_KEY = "b2b.super_user";

    @Inject
    B2BTokenUtils b2bTokenUtils;

    @ConfigProperty(name = "security.enabled", defaultValue = "true")
    boolean securityEnabled;

    @Override
    public void filter(ContainerRequestContext req) {{
        if (!securityEnabled) return;

        String authHeader = req.getHeaderString("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) return;

        String incomingToken = authHeader.substring("Bearer ".length()).trim();

        if (b2bTokenUtils.isValid(authHeader)) {{
            LOG.info("B2B SUPER_USER riconosciuto — bypass autorizzazione");
            req.setProperty(B2B_SUPER_USER_KEY, Boolean.TRUE);
        }}
    }}
}}
"""


def gen_info_yaml(sn: str, pkg: str, svc_type: str, lib_group: str, lib_artifact: str) -> str:
    """Genera il file info.yaml con i metadati del microservizio."""
    db_section = ""
    if svc_type == "datagateway":
        db_section = """\

database:
  type: mssql
  migration: flyway
  audit: hibernate-envers
  scheduler: quarkus-scheduler + shedlock
"""
    client_section = ""
    if svc_type == "frontiera":
        client_section = f"""\

rest-client:
  dg-client:
    config-key: {sn}-dg-client
    description: "Client REST verso il DataGateway corrispondente"
"""
    return f"""\
# ─────────────────────────────────────────────────────────────────────────────
# info.yaml — Metadati del microservizio (generato con scaffold PMR Quarkus)
# ─────────────────────────────────────────────────────────────────────────────

service:
  name: {sn}
  type: {svc_type}
  version: 1.0.0-SNAPSHOT
  package: {pkg}
  description: "Microservizio {svc_type} '{sn}' — pattern PMR Quarkus"

dependencies:
  common-library:
    groupId: {lib_group}
    artifactId: {lib_artifact}
    version: 1.0.0-SNAPSHOT
  quarkus-platform:
    version: 3.9.2
  java: "21"
{db_section}
kafka:
  producer:
    channel: kafka-out
    methods:
      - sendEvent(flow, topic, payload)
      - sendSerialEvent(flow, topic, messageKey, payload)
      - sendSerialEventWithHeaders(transId, keyLogic, processType, flow, topic, messageKey, payload)
      - sendEventWithHeaders(transId, keyLogic, processType, flow, topic, payload)
  consumer:
    channel: kafka-in
    description: "Aggiungere metodi @Incoming('kafka-in') in KafkaGenericConsumer"

observability:
  health: quarkus-smallrye-health
  metrics: micrometer-prometheus
  openapi: quarkus-smallrye-openapi
  logging: jboss-logging + MDC headers (TRANSACTION-ID, KEY-LOGIC, PROCESS-TYPE)
{client_section}
security:
  oidc: quarkus-oidc
"""


def gen_readme(sn: str, pkg: str, svc_type: str, lib_group: str, lib_artifact: str) -> str:
    """Genera il README.md del microservizio."""
    type_label = "Frontiera" if svc_type == "frontiera" else "DataGateway"
    type_desc = (
        "Microservizio **Frontiera**: espone API REST, si autentica via OIDC, "
        "fa da proxy verso il DataGateway corrispondente e pubblica eventi Kafka."
        if svc_type == "frontiera"
        else
        "Microservizio **DataGateway**: accede al database MSSQL, gestisce "
        "migrazioni Flyway, audit Envers, job schedulati (ShedLock) e pubblica eventi Kafka."
    )
    db_section = ""
    if svc_type == "datagateway":
        db_section = """
### Variabili d'ambiente — Database

| Variabile | Descrizione |
|---|---|
| `DB_URL` | JDBC URL del database MSSQL |
| `DB_USERNAME` | Username database |
| `DB_PASSWORD` | Password database |
"""
    client_section = ""
    if svc_type == "frontiera":
        client_section = f"""
### Client REST verso il DataGateway

Il client `SampleDgClient` (chiave `{sn}-dg-client`) punta al DataGateway.
Configurarlo in `application.properties`:

```properties
quarkus.rest-client.{sn}-dg-client.url=${{DG_URL:http://localhost:8081}}
```
"""
    kafka_section = (
        "- **Frontiera** (`RequestHeadersContext`): gli header Kafka (`TRANSACTION-ID`, `KEY-LOGIC`, `PROCESS-TYPE`) "
        "vengono propagati automaticamente dal contesto HTTP."
        if svc_type == "frontiera"
        else
        "- **DataGateway** (senza `RequestHeadersContext`): gli header vengono generati automaticamente "
        "o forniti esplicitamente tramite i metodi `*WithHeaders`."
    )
    next_steps_extra = (
        "4. Rinomina le classi `Sample*` con i nomi reali delle entità di dominio\n"
        "5. Configura i topic Kafka in `Constants.java` → interfaccia `Topic`"
        if svc_type == "frontiera"
        else
        "4. Rinomina classi `Sample*`, `*Entity`, `*Repository`, `*Mapper` con i nomi reali\n"
        "5. Aggiorna la migrazione `V1__CREATE_TABLES.sql` con le tabelle reali\n"
        "6. Configura i topic Kafka in `Constants.java` → interfaccia `Topic`"
    )
    return f"""\
# {sn}

> Microservizio **{type_label}** — pattern PMR Quarkus

{type_desc}

---

## Struttura del progetto

```
{sn}/
├── info.yaml                             ← metadati servizio
├── pom.xml
├── Dockerfile.hybrid-devops
├── src/
│   ├── main/
│   │   ├── java/{pkg.replace('.', '/')}/
│   │   │   ├── config/        ApplicationConfig, OpenApiConfig, RestApplication
│   │   │   ├── filter/        MdcHeadersFilter, GlobalHeadersOpenApiFilter{',' + chr(10) + '│   │   │   │              RequestHeadersContext' if svc_type == 'frontiera' else ''}
│   │   │   ├── health/        ApplicationHealthCheck
│   │   │   ├── kafka/         KafkaGenericProducer, KafkaGenericConsumer
│   │   │   ├── service/       TopicService{',' + chr(10) + '│   │   │   │              SampleService' if svc_type == 'frontiera' else ''}
│   │   │   ├── resource/      {'SampleResource' if svc_type == 'frontiera' else to_class_prefix(sn) + 'Resource'}
│   │   │   ├── dto/           {'SampleDTO' if svc_type == 'frontiera' else to_class_prefix(sn) + 'DTO'}
│   │   │   ├── exception/     RemoteCallException, RetryableRemoteException
│   │   │   ├── response/      GenericResponse, ResponseStatus{',' + chr(10) + '│   │   │   │              CustomResponse' if svc_type == 'frontiera' else ''}
│   │   │   └── utils/         Constants, RequestCtx, Utility, MessageTypeEnum{''.join([chr(10) + '│   │   │   ├── client/        SampleDgClient' if svc_type == 'frontiera' else '', chr(10) + '│   │   │   ├── domain/        ' + to_class_prefix(sn) + 'Entity, RevisionInfo' if svc_type == 'datagateway' else '', chr(10) + '│   │   │   ├── repository/    ' + to_class_prefix(sn) + 'Repository' if svc_type == 'datagateway' else '', chr(10) + '│   │   │   ├── mapper/        ' + to_class_prefix(sn) + 'Mapper' if svc_type == 'datagateway' else '', chr(10) + '│   │   │   └── scheduler/     ScheduledJob, ShedLockConfig' if svc_type == 'datagateway' else ''])}
│   │   └── resources/
│   │       ├── application.properties
│   │       └── db/migration/  V1__CREATE_TABLES.sql{'  ← solo DG' if svc_type == 'datagateway' else '  ← assente nel Frontiera'}
│   └── test/
│       └── resources/
│           └── application-test.properties
```

---

## Dipendenze principali

| Libreria | Coordinata |
|---|---|
| Common Library | `{lib_group}:{lib_artifact}:1.0.0-SNAPSHOT` |
| Quarkus BOM | `io.quarkus.platform:quarkus-bom:3.9.2` |
| Java | `21` |
{f'| MSSQL + JPA Panache | `quarkus-hibernate-orm-panache` |{chr(10)}| Flyway | `quarkus-flyway` |{chr(10)}| Hibernate Envers | audit storico |{chr(10)}| Quarkus Scheduler + ShedLock | job schedulati |' if svc_type == 'datagateway' else '| MapStruct | generazione mapper |'}

---

## Kafka — `KafkaGenericProducer`

{kafka_section}

### Metodi disponibili

```java
// Header automatici dal contesto
producer.sendEvent(flow, topic, payload);
producer.sendSerialEvent(flow, topic, messageKey, payload);

// Header espliciti
producer.sendSerialEventWithHeaders(transId, keyLogic, processType, flow, topic, messageKey, payload);
producer.sendEventWithHeaders(transId, keyLogic, processType, flow, topic, payload);
```

Header Kafka propagati: `TRANSACTION-ID`, `KEY-LOGIC`, `PROCESS-TYPE`, `FLOW`, `MESSAGE-KEY`, `content-type`.

---

## Configurazione

Copia e personalizza `src/main/resources/application.properties`.

Variabili d'ambiente minime:

| Variabile | Descrizione |
|---|---|
| `KAFKA_BOOTSTRAP_SERVERS` | Bootstrap server Kafka |
| `OIDC_AUTH_SERVER_URL` | URL OIDC |
| `REDIS_HOST` | Host Redis |
{db_section}
{client_section}
---

## Avvio locale

```bash
# 1. Assicurati che la common library sia installata
cd ../{lib_artifact} && mvn install

# 2. Avvia in modalità dev
cd {sn} && mvn quarkus:dev
```

L'applicazione sarà disponibile su `http://localhost:8080`.
Swagger UI: `http://localhost:8080/q/swagger-ui`
Health: `http://localhost:8080/q/health`
Metrics: `http://localhost:8080/q/metrics`

---

## Prossimi passi

1. Configura `application.properties` con i valori reali
2. Configura le variabili d'ambiente necessarie
3. Verifica la connessione al broker Kafka
{next_steps_extra}

---

> Generato con **scaffold PMR Quarkus** — pattern {type_label}
"""


def scaffold_library(lib_name: str, lib_pkg: str, output_dir: str) -> None:
    lib_group = parent_pkg(lib_pkg)
    root      = Path(output_dir) / lib_name
    java      = root / "src" / "main" / "java" / pkg_to_path(lib_pkg)
    res       = root / "src" / "main" / "resources"
    test_res  = root / "src" / "test" / "resources"

    print(f"\n📚  Scaffolding libreria '{lib_name}'")
    print(f"    groupId:    {lib_group}")
    print(f"    artifactId: {lib_name}")
    print(f"    package:    {lib_pkg}")
    print(f"📁  Output: {root}\n")

    write(root / "pom.xml",                          gen_lib_pom(lib_name, lib_group, lib_pkg))
    write(res  / "application.properties",           gen_lib_application_properties())
    write(res  / "META-INF" / "beans.xml",           gen_lib_beans_xml())
    write(test_res / "application-test.properties",  gen_lib_application_test_properties())

    write(java / "annotation"   / "AuthzRead.java",         gen_lib_authz_read(lib_pkg))
    write(java / "annotation"   / "AuthzWrite.java",        gen_lib_authz_write(lib_pkg))
    write(java / "annotation"   / "LogPmr.java",            gen_lib_log_pmr(lib_pkg))
    write(java / "request"      / "AuthzRequest.java",      gen_lib_authz_request(lib_pkg))
    write(java / "response"     / "AuthzResponse.java",     gen_lib_authz_response(lib_pkg))
    write(java / "client"       / "AuthorizationClient.java",gen_lib_authorization_client(lib_pkg))
    write(java / "service"      / "AuthzService.java",      gen_lib_authz_service(lib_pkg))
    write(java / "filter"       / "AuthzReadFilter.java",   gen_lib_authz_read_filter(lib_pkg))
    write(java / "filter"       / "AuthzWriteFilter.java",  gen_lib_authz_write_filter(lib_pkg))
    write(java / "filter"       / "B2BTokenFilter.java",    gen_lib_b2b_token_filter(lib_pkg))
    write(java / "factory"      / "AdsfM2MHeadersFactory.java", gen_lib_adsf_m2m_headers_factory(lib_pkg))
    write(java / "util"         / "AuthorizationUtils.java", gen_lib_authorization_utils(lib_pkg))
    write(java / "util"         / "B2BTokenUtils.java",     gen_lib_b2b_token_utils(lib_pkg))
    write(java / "util"         / "CacheUtils.java",        gen_lib_cache_utils(lib_pkg))
    write(java / "util"         / "JsonUtils.java",         gen_json_utils(f"{lib_pkg}.util"))
    write(java / "client"       / "DataPlatformClient.java",gen_lib_data_platform_client(lib_pkg))
    write(java / "config"       / "CustomHttpClient.java",  gen_lib_custom_http_client(lib_pkg))
    write(java / "cache"        / "AdsfTokenCache.java",    gen_lib_adsf_token_cache(lib_pkg))
    write(java / "dto"          / "AdsfTokenDto.java",      gen_lib_adsf_token_dto(lib_pkg))
    write(java / "service"      / "AdsfTokenService.java",  gen_lib_adsf_token_service(lib_pkg))
    write(java / "service"      / "AdsfRestClientService.java", gen_lib_adsf_rest_client_service(lib_pkg))
    write(java / "interceptor"  / "LogPmrInterceptor.java", gen_lib_log_pmr_interceptor(lib_pkg))
    write(java / "resolver"     / "MinimalContextResolver.java", gen_lib_minimal_context_resolver(lib_pkg))
    write(java / "resolver"     / "JwtUserIdResolver.java", gen_lib_jwt_user_id_resolver(lib_pkg))
    write(java / "resolver"     / "JwtRolesResolver.java",  gen_lib_jwt_roles_resolver(lib_pkg))

    print(f"\n✅  Libreria scaffoldata → {root}")
    print(f"    Installa nel repo Maven locale prima di buildare il microservizio:")
    print(f"    cd {root} && mvn install\n")


def scaffold_service_dg(sn: str, pkg: str, output_dir: str,
                        lib_group: str, lib_artifact: str, lib_pkg: str) -> None:
    root      = Path(output_dir) / sn
    java      = root / "src" / "main" / "java" / pkg_to_path(pkg)
    res       = root / "src" / "main" / "resources"
    test_res  = root / "src" / "test" / "resources"

    print(f"\n⚙️   Scaffolding microservizio DataGateway '{sn}'")
    print(f"    package:  {pkg}")
    print(f"    libreria: {lib_group}:{lib_artifact}")
    print(f"📁  Output: {root}\n")

    write(root / "pom.xml",                                       gen_pom_dg(sn, pkg, lib_group, lib_artifact))
    write(root / "Dockerfile.hybrid-devops",                      gen_svc_dockerfile(sn))
    write(res  / "application.properties",                        gen_application_properties_dg(sn, pkg, lib_pkg))
    write(test_res / "application-test.properties",               gen_application_test_properties_dg())
    write(res  / "db" / "migration" / "V1__CREATE_TABLES.sql",   gen_flyway_migration(sn))

    write(java / "utils"     / "Constants.java",                  gen_constants_dg(pkg, sn))
    write(java / "utils"     / "RequestCtx.java",                 gen_request_ctx(pkg))
    write(java / "utils"     / "Utility.java",                    gen_utility_dg(pkg))
    write(java / "utils"     / "MessageTypeEnum.java",            gen_message_type_enum(pkg))

    write(java / "exception" / "RemoteCallException.java",        gen_remote_call_exception(pkg))

    write(java / "filter"    / "MdcHeadersFilter.java",           gen_mdc_filter_dg(pkg))
    write(java / "filter"    / "GlobalHeadersOpenApiFilter.java",  gen_global_openapi_filter(pkg))

    write(java / "config"    / "ApplicationConfig.java",          gen_application_config(pkg))
    write(java / "config"    / "OpenApiConfig.java",              gen_openapi_config(pkg, sn))
    write(java / "config"    / "RestApplication.java",            gen_rest_application(pkg))

    write(java / "health"    / "ApplicationHealthCheck.java",     gen_health_check(pkg))

    write(java / "kafka"     / "KafkaGenericProducer.java",       gen_kafka_producer_dg(pkg, lib_pkg))
    write(java / "kafka"     / "KafkaGenericConsumer.java",       gen_kafka_consumer_dg(pkg, sn))
    write(java / "kafka"     / "DevKafkaTopicInitializer.java",   gen_dev_kafka_topic_initializer(pkg))

    write(java / "service"   / "TopicService.java",               gen_topic_service(pkg))
    write(java / "service"   / f"{to_class_prefix(sn)}Service.java", gen_sample_service_dg(pkg, sn, lib_pkg))

    write(java / "domain"    / f"{to_class_prefix(sn)}Entity.java", gen_domain_entity(pkg, sn))
    write(java / "domain"    / "RevisionInfo.java",               gen_revision_info(pkg))
    write(java / "repository"/ f"{to_class_prefix(sn)}Repository.java", gen_repository(pkg, sn))
    write(java / "mapper"    / f"{to_class_prefix(sn)}Mapper.java",     gen_mapper(pkg, sn))
    write(java / "dto"       / f"{to_class_prefix(sn)}DTO.java",        gen_sample_dto_dg(pkg, sn))
    write(java / "resource"  / f"{to_class_prefix(sn)}Resource.java",   gen_sample_resource_dg(pkg, sn, lib_pkg))

    write(java / "scheduler" / "ScheduledJob.java",               gen_scheduled_job(pkg, sn))
    write(java / "scheduler" / "ShedLockConfig.java",             gen_shedlock_config(pkg))

    write(root / "info.yaml",                                      gen_info_yaml(sn, pkg, "datagateway", lib_group, lib_artifact))
    write(root / "README.md",                                      gen_readme(sn, pkg, "datagateway", lib_group, lib_artifact))

    print(f"\n✅  Microservizio DataGateway scaffoldato → {root}")


def scaffold_service(sn: str, pkg: str, output_dir: str,
                     lib_group: str, lib_artifact: str, lib_pkg: str) -> None:
    root      = Path(output_dir) / sn
    java      = root / "src" / "main" / "java" / pkg_to_path(pkg)
    res       = root / "src" / "main" / "resources"
    test_res  = root / "src" / "test" / "resources"

    print(f"\n⚙️   Scaffolding microservizio '{sn}'")
    print(f"    package:  {pkg}")
    print(f"    libreria: {lib_group}:{lib_artifact}")
    print(f"📁  Output: {root}\n")

    write(root / "pom.xml",                                    gen_pom(sn, pkg, lib_group, lib_artifact))
    write(root / "Dockerfile.hybrid-devops",                   gen_svc_dockerfile(sn))
    write(res  / "application.properties",                     gen_application_properties(sn, pkg, lib_pkg))
    write(test_res / "application-test.properties",            gen_application_test_properties_svc(sn))

    write(java / "utils"    / "Constants.java",                gen_constants(pkg, sn))
    write(java / "utils"    / "RequestCtx.java",               gen_request_ctx(pkg))
    write(java / "utils"    / "Utility.java",                  gen_utility(pkg))
    write(java / "utils"    / "MessageTypeEnum.java",          gen_message_type_enum(pkg))

    write(java / "exception"/ "RemoteCallException.java",      gen_remote_call_exception(pkg))
    write(java / "exception"/ "RetryableRemoteException.java", gen_retryable_remote_exception(pkg))

    write(java / "response" / "GenericResponse.java",          gen_generic_response(pkg))
    write(java / "response" / "ResponseStatus.java",           gen_response_status(pkg))
    write(java / "response" / "CustomResponse.java",           gen_custom_response(pkg))

    write(java / "filter"   / "RequestHeadersContext.java",    gen_request_headers_context(pkg))
    write(java / "filter"   / "MdcHeadersFilter.java",         gen_mdc_filter(pkg))
    write(java / "filter"   / "GlobalHeadersOpenApiFilter.java",gen_global_openapi_filter(pkg))
    write(java / "filter"   / "RestClientHeadersFilter.java",  gen_rest_client_headers_filter(pkg))

    write(java / "config"   / "ApplicationConfig.java",        gen_application_config(pkg))
    write(java / "config"   / "OpenApiConfig.java",            gen_openapi_config(pkg, sn))
    write(java / "config"   / "RestApplication.java",          gen_rest_application(pkg))

    write(java / "health"   / "ApplicationHealthCheck.java",   gen_health_check(pkg))

    write(java / "kafka"    / "KafkaGenericProducer.java",     gen_kafka_producer(pkg, lib_pkg))
    write(java / "kafka"    / "KafkaGenericConsumer.java",     gen_kafka_consumer(pkg))
    write(java / "kafka"    / "DevKafkaTopicInitializer.java", gen_dev_kafka_topic_initializer(pkg))

    write(java / "service"  / "TopicService.java",             gen_topic_service(pkg))
    write(java / "service"  / "SampleService.java",            gen_sample_service(pkg, lib_pkg))
    write(java / "client"   / "SampleDgClient.java",           gen_sample_client(pkg, sn))
    write(java / "dto"      / "SampleDTO.java",                gen_sample_dto(pkg))
    write(java / "resource" / "SampleResource.java",           gen_sample_resource(pkg, sn, lib_pkg))

    write(root / "info.yaml",                                   gen_info_yaml(sn, pkg, "frontiera", lib_group, lib_artifact))
    write(root / "README.md",                                   gen_readme(sn, pkg, "frontiera", lib_group, lib_artifact))

    print(f"\n✅  Microservizio scaffoldato → {root}")


# ═════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold Quarkus microservice + common library (pattern PMR).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  # Microservizio Frontiera (usa pmr-common-library di default)
  scaffold_quarkus.py -s my-svc -p it.eng.myorg.mysvc

  # Microservizio DataGateway (suffisso -dg)
  scaffold_quarkus.py --type datagateway -s my-svc-dg -p it.eng.myorg.mysvcdg

  # Microservizio + libreria custom (generate e collegate)
  scaffold_quarkus.py -s my-svc -p it.eng.myorg.mysvc \\
                      --lib-name my-lib --lib-package it.eng.myorg.common

  # Solo libreria
  scaffold_quarkus.py --lib-only --lib-name my-lib --lib-package it.eng.myorg.common
"""
    )
    parser.add_argument("--service-name",  "-s", help="Nome microservizio (kebab-case)")
    parser.add_argument("--base-package",  "-p", help="Package Java del microservizio")
    parser.add_argument("--type",          "-t", choices=["frontiera", "datagateway"],
                        default="frontiera",
                        help="Tipo microservizio: 'frontiera' (REST proxy, default) o 'datagateway' (DB+scheduler)")
    parser.add_argument("--lib-name",            help="Nome libreria comune (kebab-case)")
    parser.add_argument("--lib-package",         help="Package Java della libreria comune")
    parser.add_argument("--lib-only",            action="store_true", help="Genera solo la libreria")
    parser.add_argument("--output-dir",    "-o", default=".", help="Directory di output (default: .)")
    args = parser.parse_args()

    out = args.output_dir.strip()

    # ── Validazioni ──────────────────────────────────────────────────────────
    def valid_name(v):  return bool(re.match(r'^[a-z][a-z0-9\-_]*$', v))
    def valid_pkg(v):   return bool(re.match(r'^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)+$', v))

    if args.lib_only:
        if not args.lib_name or not args.lib_package:
            print("❌  --lib-only richiede --lib-name e --lib-package", file=sys.stderr); sys.exit(1)
        if not valid_name(args.lib_name):
            print("❌  --lib-name deve essere kebab-case", file=sys.stderr); sys.exit(1)
        if not valid_pkg(args.lib_package):
            print("❌  --lib-package non è un package Java valido", file=sys.stderr); sys.exit(1)
        scaffold_library(args.lib_name.strip(), args.lib_package.strip(), out)
        return

    if not args.service_name or not args.base_package:
        print("❌  Specificare --service-name e --base-package (o usare --lib-only)", file=sys.stderr); sys.exit(1)
    if not valid_name(args.service_name):
        print("❌  --service-name deve essere kebab-case", file=sys.stderr); sys.exit(1)
    if not valid_pkg(args.base_package):
        print("❌  --base-package non è un package Java valido", file=sys.stderr); sys.exit(1)

    # ── Risolvi coordinate libreria ──────────────────────────────────────────
    has_custom_lib = bool(args.lib_name and args.lib_package)

    if has_custom_lib:
        if not valid_name(args.lib_name):
            print("❌  --lib-name deve essere kebab-case", file=sys.stderr); sys.exit(1)
        if not valid_pkg(args.lib_package):
            print("❌  --lib-package non è un package Java valido", file=sys.stderr); sys.exit(1)
        lib_name    = args.lib_name.strip()
        lib_pkg     = args.lib_package.strip()
        lib_group   = parent_pkg(lib_pkg)
        lib_artifact = lib_name
    else:
        lib_group    = DEFAULT_LIB_GROUP
        lib_artifact = DEFAULT_LIB_ARTIFACT
        lib_pkg      = DEFAULT_LIB_PKG

    # ── Genera ───────────────────────────────────────────────────────────────
    if has_custom_lib:
        scaffold_library(lib_name, lib_pkg, out)

    if args.type == "datagateway":
        scaffold_service_dg(args.service_name.strip(), args.base_package.strip(), out,
                            lib_group, lib_artifact, lib_pkg)
    else:
        scaffold_service(args.service_name.strip(), args.base_package.strip(), out,
                         lib_group, lib_artifact, lib_pkg)

    # ── Riepilogo ────────────────────────────────────────────────────────────
    svc_root = Path(out) / args.service_name.strip()
    print("\n📋  Prossimi passi:")
    if has_custom_lib:
        lib_root = Path(out) / lib_name
        print(f"  1. cd {lib_root} && mvn install     ← installa la libreria")
        print(f"  2. cd {svc_root} && mvn quarkus:dev ← avvia il microservizio")
    else:
        print(f"  1. Assicurati che {DEFAULT_LIB_ARTIFACT} sia installata: mvn install")
        print(f"  2. cd {svc_root} && mvn quarkus:dev")
    if args.type == "datagateway":
        print("  3. Rinomina le classi Sample/Entity con i nomi reali del dominio")
        print("  4. Configura topic Kafka in Constants.java → Interface Topic")
        print("  5. Verifica la migrazione Flyway in src/main/resources/db/migration/")
        print("  6. Configura datasource (DB_URL, DB_USERNAME, DB_PASSWORD)")
    else:
        print("  3. Rinomina le classi Sample* con i nomi reali delle entità")
        print("  4. Configura topic Kafka in Constants.java → Interface Topic")
    print()


if __name__ == "__main__":
    main()
