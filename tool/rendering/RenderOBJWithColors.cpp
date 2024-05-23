#include <GL/glew.h>
#include <GL/freeglut.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <png.h>

struct Vertex {
    float x, y, z;    // Vertex coordinates
    float r, g, b;    // Vertex colors
};

std::vector<Vertex> vertices;
std::vector<unsigned int> indices; // Indices for faces

// Function to save the current OpenGL render window to a PNG file
void saveOpenGLBufferToPNG(const char* filename) {
    GLint viewport[4];
    glGetIntegerv(GL_VIEWPORT, viewport);
    int width = viewport[2];
    int height = viewport[3];

    auto* buffer = new unsigned char[width * height * 3];
    glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE, buffer);

    FILE* fp = fopen(filename, "wb");
    if (!fp) return;

    png_structp png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, nullptr, nullptr, nullptr);
    if (!png_ptr) return;

    png_infop info_ptr = png_create_info_struct(png_ptr);
    if (!info_ptr) return;

    png_init_io(png_ptr, fp);
    png_set_IHDR(png_ptr, info_ptr, width, height,
                 8, PNG_COLOR_TYPE_RGB, PNG_INTERLACE_NONE,
                 PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);
    png_write_info(png_ptr, info_ptr);

    for (int y = 0; y < height; y++) {
        png_write_row(png_ptr, buffer + (height - 1 - y) * width * 3);
    }

    png_write_end(png_ptr, nullptr);
    fclose(fp);

    delete[] buffer;
    png_destroy_write_struct(&png_ptr, &info_ptr);
}

// Function to load an OBJ file
bool loadOBJ(const char* path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "Unable to open file: " << path << std::endl;
        return false;
    }
    std::string line;
    while (getline(file, line)) {
        std::istringstream iss(line);
        std::string prefix;
        iss >> prefix;
        if (prefix == "v") {
            Vertex vertex;
            iss >> vertex.x >> vertex.y >> vertex.z >> vertex.r >> vertex.g >> vertex.b;
            vertices.push_back(vertex);
        } else if (prefix == "f") {
            unsigned int vertexIndex[3];
            iss >> vertexIndex[0] >> vertexIndex[1] >> vertexIndex[2];
            indices.push_back(vertexIndex[0] - 1);
            indices.push_back(vertexIndex[1] - 1);
            indices.push_back(vertexIndex[2] - 1);
        }
    }
    return true;
}

// OpenGL initialization
void initOpenGL(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize(800, 600);
    glutCreateWindow("OBJ with Vertex Colors");
    glewInit();
}

// Rendering scene
void renderScene() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glEnable(GL_DEPTH_TEST);
    
    glBegin(GL_TRIANGLES);
    for (size_t i = 0; i < indices.size(); i++) {
        Vertex& v = vertices[indices[i]];
        glColor3f(v.r, v.g, v.b);
        glVertex3f(v.x, v.y, v.z);
    }
    glEnd();

    glutSwapBuffers();
}

// Function to be called after the main loop to save the frame
void onExit() {
    saveOpenGLBufferToPNG("output.png");
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <OBJ File Path>" << std::endl;
        return 1;
    }

    if (!loadOBJ(argv[1])) {
        return 1;
    }

    initOpenGL(argc, argv);
    glutDisplayFunc(renderScene);
    atexit(onExit); // Register exit function
    glutMainLoop();

    return 0;
}

// g++ -o RenderOBJWithColors /mnt/chenjh/Idea23D/tool/rendering/RenderOBJWithColors.cpp -lGLEW -lglut -lGL -lpng
// ./RenderOBJWithColors /mnt/chenjh/Idea23D/input/0/mesh.obj
