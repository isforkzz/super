# SuperStaticLanguage

<p align="center">
  <strong>A modern, statically-typed scripting language built in Python.</strong><br/>
  Write <code>.ssl</code> files. Run them with <code>super</code>.
</p>

---

## Installation

```bash
pip install super
```

---

## Quick Start

```bash
super init -y    # scaffold a new project
super .          # run your project
```

This creates a `super.json` and a `main.ssl` ready to go.

---

## CLI Commands

| Command | Description |
|---|---|
| `super init` | Create `super.json` and `main.ssl` interactively |
| `super init -y` | Skip prompts, create with defaults |
| `super .` | Run the `main` file defined in `super.json` |
| `super <file.ssl>` | Run a specific `.ssl` file |
| `super execute <script>` | Run a named script from `super.json` |
| `super version` | Print the runner version |

---

## super.json

```json
{
    "main": "main.ssl",
    "scripts": {
        "dev": "dev.ssl",
        "build": "build.ssl"
    },
    "packages": {},
    "type": "default"
}
```

---

## Language

### Variables

```ssl
const name: string = "SSL"
var age: int = 1
let price: float = 9.99
const active: bool = true
const tags: array = ["fast", "typed", "simple"]
```

Typing is optional:
```ssl
const x = 42
const msg = "hello"
```

### Template Strings

```ssl
const lang = "SSL"
const version = 1
console.log(f"${lang} v${version} is running!")
```

### Functions

```ssl
function add(a: int, b: int): int {
    return a + b
}

async function fetch(url: string) {
    return url
}
```

### Arrow Functions

```ssl
const double = (x: int): int => {
    return x * 2
}

const greet = (name: string) => {
    console.log(f"Hello, ${name}!")
}

// async arrow
const load = async (id: int) => {
    return id
}

// IIFE
(async () => {
    console.log("running!")
})()
```

### Classes

```ssl
class Animal {
    name: string
    sound: string

    constructor(name: string, sound: string) {
        this.name = name
        this.sound = sound
    }

    public function speak() {
        console.log(f"${this.name} says ${this.sound}!")
    }

    private function _internal() {
        return true
    }
}

class Dog extends Animal {
    constructor(name: string) {
        super(name, "woof")
    }
}

const dog = new Dog("Rex")
dog.speak()   // Rex says woof!
```

### Interfaces & Types

```ssl
interface User {
    name: string
    age: int
    active: bool
}

// union type
type Status = "active" | "inactive" | "banned"
type Channel = TextChannel | VoiceChannel
```

### Enums

```ssl
enum Direction {
    North
    South
    East
    West
}

const dir = Direction.North
```

### Control Flow

```ssl
// if / else
if (x > 10) {
    console.log("big")
} else {
    console.log("small")
}

// match
match (status) {
    case "active"   { console.log("online") }
    case "banned"   { console.log("blocked") }
    default         { console.log("unknown") }
}

// for
for (item in list) {
    console.log(item)
}

// range
for (i in range(0, 10)) {
    console.log(i)
}

// while
while (x > 0) {
    x -= 1
}

// ternary
const label = x > 0 ? "positive" : "zero or negative"
```

### Error Handling

```ssl
try {
    const result = riskyCall()
} except (TypeError) {
    console.log("wrong type!")
} except (Error) {
    console.log("something went wrong")
}
```

### Array Methods

```ssl
const nums = [1, 2, 3, 4, 5]

const doubled = nums.map((x) => { return x * 2 })
const evens   = nums.filter((x) => { return x % 2 == 0 })
const found   = nums.find((x) => { return x > 3 })
const total   = nums.length()

nums.push(6)
const last = nums.pop()
const has3 = nums.includes(3)
```

### String Methods

```ssl
const s = "  Hello World  "

s.toUpper()              // "  HELLO WORLD  "
s.toLower()              // "  hello world  "
s.trim()                 // "Hello World"
s.replace("World", "SSL")
s.length()               // 15
s.parseInt()             // for numeric strings
s.parseFloat()
```

### Number Methods

```ssl
const n = 9.9912

n.toFixed(2)   // 9.99
n.toString()   // "9.9912"
n.parseInt()   // 9
```

### Objects

```ssl
const user = { name: "João", age: 17 }

user.name                            // "João"
user.get("name")                     // "João"
user.get("address", {}).get("city")  // safe nested access
user?.address?.city                  // optional chaining
user.name ?? "anonymous"             // nullish coalescing

delete user.age
```

### Destructuring & Spread

```ssl
const { name, age } = user
const [first, ...rest] = list
const merged = [...list1, ...list2, 99]
```

### Operators

```ssl
// arithmetic
x + y   x - y   x * y   x / y   x % y   x ** y

// assignment
x += 1   x -= 1   x *= 2   x /= 2   x %= 3   x **= 2

// comparison
==   !=   >   <   >=   <=

// logical
and   or   is   is not

// type check
if (x is string) { }
if (x is not int) { }
```

### Utilities

```ssl
typeof x      // "string", "int", "float", "bool", "array", "object"
exists(x)     // true if x is defined and not null
delete obj.key
```

### Imports & Exports

```ssl
// export a variable
export const VERSION = "1.0.0"

// register a page alias (place at end of file)
export page as "#mylib"
export page as "@utils"

// import
import * from 'path/to/file'
import { VERSION } from 'path/to/file'
import { helper } from '#mylib'
import { fn } from '@utils'
```

### Global Scope

```ssl
global const APP_NAME = "MyApp"

global function log(msg: string) {
    console.log(f"[${APP_NAME}] ${msg}")
}

global async function init() {
    console.log("initializing...")
}
```

### Decorators

```ssl
// simple function decorator
function readonly(fn) {
    return () => { return fn() }
}

@readonly
function getValue(): int {
    return 42
}

// class-defined decorators
class Client {
    Decorator on(event: string) {
        // register handler
    }
}

const client = new Client()

@client.on("ready")
async function onReady() {
    console.log("online!")
}

@client.on("message")
async function onMessage(msg) {
    console.log(msg)
}
```

### Comments

```ssl
// single line comment

/$
  multi
  line
  comment
$/
```

---

## Built-ins

| Name | Description |
|---|---|
| `console.log(...)` | Print to stdout |
| `console.warn(...)` | Print warning |
| `console.error(...)` | Print error |
| `console.info(...)` | Print info |
| `print(...)` | Alias for console.log |
| `range(start, end)` | Generate integer range |
| `typeof x` | Returns type name as string |
| `exists(x)` | Check if variable is defined and not null |

---

## License

MIT © SuperStaticLanguage
