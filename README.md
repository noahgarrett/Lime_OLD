# Lime
The GenZ Approved programming language alternative, JIT compiled by the dragon himself... LLVM

## GenZ Approved Features
Normal language keywords have alternates for the gen z people to feel safe.
- `fn` -> `bruh` | `bruh main() { }`
- `return` -> `pause` | `bruh main() { pause 1; }`
- `;` -> `rn` | `=` -> `be` | `let` -> `lit`
- `if/else` -> `sus/imposter`
- `trans` -> `import`
- `ass` -> `class`
- `export` -> `yeet`
```js
// Example Lime Pallet `pallet.lime`
yeet bruh gimme_42() -> int {
    pause 42 rn
}
```

```js
// Example GenZ Approved Program `main.lime`
from "pallet.lime" trans gimmie_42 rn

ass Box { // **Classes Under Development**
    bruh __init__() -> void {
        
    }
}

bruh main() -> int {
    lit a: int be 25 rn

    sus a == 25 {
        printf("oh boi %i\n", gimmie_42()) rn
    } imposter {
        printf("yesssssir") rn
    }

    pause a rn
}
```

## Tests
- Mandelbrot Set script `src/debug/mandel.lime`
![Mandelbrot](mandel_example.png)

## Features so far
- Every program must have a `main` function defined and it must return an integer code
```js
fn main() -> int {
    return 1;
}
```

- Datatypes
    - int
    - float
    - str
    - void

- Function Definitions + Function Calling
    - **TEMP** Strings are not allowed to be returned from functions. Working out a bug here
```js
fn add(a: int, b: int) -> int {
    return a + b;
}

fn main() -> int {
    return add(1, 2);
}
```

- Variable Assignment + Re-assignment
```js
fn main() -> int {
    let a: int = 25;
    a = 5;

    return a;
}
```

- Basic Arithmetic (+-*/)
```js
fn main() -> int {
    let a: float = 1 + 2 - 3 * 4 / (4 - 2);

    return a;
}
```

- Built-in Functions
    - `printf` (C-like printf function)
```js
fn main() -> int {
    printf("I have %i apples..", 69);
    
    return 1;
}
```

- Loops
    - While Loops
```js
fn main() -> int {
    let a: int = 25;

    while a < 50 {
        a = a + 1;
        printf("yeet: %i\n", a);
    }

    return a;
}
```

- Conditionals
```js
fn main() -> int {
    let a: int = 0;

    if a == 0 {
        printf("A BE ZERO");
    } else {
        printf("NO ZERO HERE");
    }

    return 0;
}
```

- Imports
    - Currently it globally imports all functions and variables
```js
import "./pallet.lime"
```

- From Imports
```js
from "./pallet.lime" import gimme_42
```

- Exporting from files / pallets
```js
export fn add(a: int, b: int) -> int {
    return a + b;
}

export fn sub(a: int, b: int) -> int {
    return a - b;
}
export let CONSTANT_VARIABLE: int = 69; // STILL UNDER DEVELOPMENT FOR VARIABLES
```
