import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.util.Base64

val MAX_SAFE_INTEGER = 9007199254740991L

sealed interface JsonValue
data object JsonNull : JsonValue
data class JsonBoolean(val value: Boolean) : JsonValue
data class JsonInteger(val value: Long) : JsonValue {
    init {
        require(value in -MAX_SAFE_INTEGER..MAX_SAFE_INTEGER) {
            "Canonical JSON supports safe integers only"
        }
    }
}
data class JsonString(val value: String) : JsonValue
data class JsonArray(val values: List<JsonValue>) : JsonValue
data class JsonObject(val values: Map<String, JsonValue>) : JsonValue

fun requireUnicodeScalarString(value: String) {
    var index = 0
    while (index < value.length) {
        val character = value[index]
        when {
            character.isHighSurrogate() -> {
                require(index + 1 < value.length && value[index + 1].isLowSurrogate()) {
                    "Canonical JSON rejects unpaired UTF-16 surrogates"
                }
                index += 2
            }
            character.isLowSurrogate() -> error(
                "Canonical JSON rejects unpaired UTF-16 surrogates"
            )
            else -> index += 1
        }
    }
}

fun quote(value: String): String {
    requireUnicodeScalarString(value)
    return buildString {
        append('"')
        value.forEach { character ->
            when (character) {
                '"' -> append("\\\"")
                '\\' -> append("\\\\")
                '\b' -> append("\\b")
                '\u000C' -> append("\\f")
                '\n' -> append("\\n")
                '\r' -> append("\\r")
                '\t' -> append("\\t")
                else -> if (character.code < 0x20) {
                    append("\\u%04x".format(character.code))
                } else {
                    append(character)
                }
            }
        }
        append('"')
    }
}

val codePointComparator = Comparator<String> { left, right ->
    requireUnicodeScalarString(left)
    requireUnicodeScalarString(right)
    val leftPoints = left.codePoints().toArray()
    val rightPoints = right.codePoints().toArray()
    val length = minOf(leftPoints.size, rightPoints.size)
    for (index in 0 until length) {
        if (leftPoints[index] != rightPoints[index]) {
            return@Comparator leftPoints[index] - rightPoints[index]
        }
    }
    leftPoints.size - rightPoints.size
}

fun canonicalize(value: JsonValue): String = when (value) {
    JsonNull -> "null"
    is JsonBoolean -> value.value.toString()
    is JsonInteger -> value.value.toString()
    is JsonString -> quote(value.value)
    is JsonArray -> value.values.joinToString(prefix = "[", postfix = "]", separator = ",", transform = ::canonicalize)
    is JsonObject -> value.values.keys.sortedWith(codePointComparator).joinToString(
        prefix = "{",
        postfix = "}",
        separator = ","
    ) { key -> "${quote(key)}:${canonicalize(value.values.getValue(key))}" }
    else -> error("Unsupported JSON value")
}

fun hash(canonical: String): String = Base64.getUrlEncoder()
    .withoutPadding()
    .encodeToString(MessageDigest.getInstance("SHA-256").digest(canonical.toByteArray(StandardCharsets.UTF_8)))

fun protectedOperation(
    projectId: String,
    challengeId: String,
    operation: String,
    arguments: Map<String, JsonValue>
): JsonObject = JsonObject(mapOf(
    "project_id" to JsonString(projectId),
    "contract_version" to JsonString("digitalis.v1"),
    "challenge_id" to JsonString(challengeId),
    "operation" to JsonString(operation),
    "operation_arguments" to JsonObject(arguments)
))

data class Vector(val name: String, val operation: JsonObject, val canonical: String, val requestHash: String)

val vectors = listOf(
    Vector(
        "configuration-bootstrap",
        protectedOperation(
            "11111111-1111-4111-8111-111111111111",
            "22222222-2222-4222-8222-222222222222",
            "configuration.bootstrap",
            mapOf(
                "environment" to JsonString("production"),
                "requested_capabilities" to JsonArray(listOf(JsonString("protected_config")))
            )
        ),
        "{\"challenge_id\":\"22222222-2222-4222-8222-222222222222\",\"contract_version\":\"digitalis.v1\",\"operation\":\"configuration.bootstrap\",\"operation_arguments\":{\"environment\":\"production\",\"requested_capabilities\":[\"protected_config\"]},\"project_id\":\"11111111-1111-4111-8111-111111111111\"}",
        "1D1YEavcto7xBFBW-dPcXEr6iyIq8aowGSR68poH7lk"
    ),
    Vector(
        "transaction-authorize",
        protectedOperation(
            "11111111-1111-4111-8111-111111111111",
            "33333333-3333-4333-8333-333333333333",
            "transaction.authorize",
            mapOf(
                "merchant" to JsonObject(mapOf("id" to JsonString("merchant-42"), "country" to JsonString("US"))),
                "requires_user_presence" to JsonBoolean(true),
                "currency" to JsonString("USD"),
                "amount_minor" to JsonInteger(1250)
            )
        ),
        "{\"challenge_id\":\"33333333-3333-4333-8333-333333333333\",\"contract_version\":\"digitalis.v1\",\"operation\":\"transaction.authorize\",\"operation_arguments\":{\"amount_minor\":1250,\"currency\":\"USD\",\"merchant\":{\"country\":\"US\",\"id\":\"merchant-42\"},\"requires_user_presence\":true},\"project_id\":\"11111111-1111-4111-8111-111111111111\"}",
        "7ilO_sgIty0Nz2QUW06oe_bmhxYaCXfxF01GdhdbN0A"
    ),
    Vector(
        "unicode-and-nested-values",
        protectedOperation(
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
            "configuration.bootstrap",
            mapOf(
                "sequence" to JsonArray(listOf(JsonInteger(3), JsonInteger(2), JsonInteger(1))),
                "metadata" to JsonObject(mapOf("null_value" to JsonNull, "emoji" to JsonString("🔐"))),
                "label" to JsonString("café")
            )
        ),
        "{\"challenge_id\":\"bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb\",\"contract_version\":\"digitalis.v1\",\"operation\":\"configuration.bootstrap\",\"operation_arguments\":{\"label\":\"café\",\"metadata\":{\"emoji\":\"🔐\",\"null_value\":null},\"sequence\":[3,2,1]},\"project_id\":\"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa\"}",
        "MYDh8iljMqp-VgQNBb5G1W5UlOCBGtgTQRbEc5wK0NE"
    ),
    Vector(
        "unicode-code-point-key-order-and-escaping",
        protectedOperation(
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
            "configuration.bootstrap",
            mapOf(
                "💡" to JsonString("supplementary"),
                "\uE000" to JsonString("bmp-private-use"),
                "escaped" to JsonString("line\nquote\"slash\\")
            )
        ),
        "{\"challenge_id\":\"cccccccc-cccc-4ccc-8ccc-cccccccccccc\",\"contract_version\":\"digitalis.v1\",\"operation\":\"configuration.bootstrap\",\"operation_arguments\":{\"escaped\":\"line\\nquote\\\"slash\\\\\",\"\uE000\":\"bmp-private-use\",\"💡\":\"supplementary\"},\"project_id\":\"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa\"}",
        "nps1PSB9tmrNwAPU0xwjRTk51sQarcpm9i9dfHVDYDQ"
    )
)

vectors.forEach { vector ->
    val canonical = canonicalize(vector.operation)
    check(canonical == vector.canonical) { "${vector.name}: canonical bytes differ" }
    check(hash(canonical) == vector.requestHash) { "${vector.name}: request hash differs" }
}

check(runCatching { JsonInteger(MAX_SAFE_INTEGER + 1) }.isFailure) {
    "Kotlin verifier must reject integers outside the JavaScript safe-integer range"
}
check(runCatching { quote("\uD800") }.isFailure) {
    "Kotlin verifier must reject unpaired UTF-16 surrogates"
}

println("Digitalis Kotlin canonical request vectors passed: ${vectors.size}")
