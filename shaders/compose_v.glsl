//GLSL
#version 110
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * gl_Vertex; 
    gl_TexCoord[0] = gl_Position*0.5+0.5;
    }