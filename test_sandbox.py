from backend.tools.docker_sandbox import execute_code


print("\n==============================")
print("PYTHON TEST")
print("==============================")

print(
    execute_code(
        """
print("Hello from Python")
""",
        "python"
    )
)


print("\n==============================")
print("JAVASCRIPT TEST")
print("==============================")

print(
    execute_code(
        """
console.log("Hello from JavaScript");
""",
        "javascript"
    )
)


print("\n==============================")
print("JAVA TEST")
print("==============================")

print(
    execute_code(
        """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java");
    }
}
""",
        "java"
    )
)


print("\n==============================")
print("C++ TEST")
print("==============================")

print(
    execute_code(
        """
#include <iostream>

int main() {
    std::cout << "Hello from C++" << std::endl;
    return 0;
}
""",
        "cpp"
    )
)


print("\n==============================")
print("C TEST")
print("==============================")

print(
    execute_code(
        """
#include <stdio.h>

int main() {
    printf("Hello from C\\n");
    return 0;
}
""",
        "c"
    )
)