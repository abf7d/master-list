# Libraries Folder (`libs`)

This folder contains libraries used in the Angular application. Libraries can be categorized as **publishable** or **non-publishable**.

## Library Types

### 1. Publishable Libraries
- **Purpose**: These libraries are designed to be shared across multiple projects or published to a package registry (e.g., npm).
- **Creation**: Use the Angular CLI to scaffold publishable libraries. This ensures proper configuration in `angular.json` and other necessary files.
  ```bash
  ng generate library <library-name>
  ```
- **Build Properties**: Publishable libraries include detailed build configurations in `angular.json`.

### 2. Non-Publishable Libraries
- **Purpose**: These libraries are used internally within the project and are not intended for external distribution.
- **Creation**: Manually add an entry in the `angular.json` file. Below is an example configuration:
  ```json
  "lists": {
    "projectType": "library",
    "root": "projects/libs/lists",
    "sourceRoot": "projects/libs/lists/src",
    "prefix": "ml",
    "schematics": {
      "@schematics/angular:component": {
        "standalone": true,
        "skipImport": true,
        "style": "scss"
      }
    },
    "targets": {}
  }
  ```
  - **Key Points**:
    - `root`: Path to the library folder.
    - `sourceRoot`: Path to the `src` folder inside the library.
    - `prefix`: Prefix for Angular component selectors.
    - `schematics`: Default options for generating components within the library.

## Existing Libraries

### 1. `auth`
- **Type**: Legacy
- **Purpose**: Handles authentication-related functionality.

### 2. `environments`
- **Type**: Legacy
- **Purpose**: Manages environment-specific configurations.

## Guidelines for Adding New Libraries

1. **Publishable Libraries**:
   - Use the Angular CLI to generate the library.
   - Ensure proper build configurations are added automatically.

2. **Non-Publishable Libraries**:
   - Create a folder under `projects/libs/`.
   - Add a `src` folder inside the library folder.
   - Update the `angular.json` file with a minimal configuration (see example above).

3. **General**:
   - Use meaningful names for libraries.
   - Follow the Angular style guide for consistency.
   - Use `scss` for styles unless otherwise specified.

## Notes
- Always test libraries thoroughly before integrating them into the application.
- For publishable libraries, ensure proper versioning and documentation.

