//GLSL
#version 110
uniform sampler2D glareTex;

varying vec2 uv;

void main() 
    {    
    int NSAMPLES = 5;
    float FLARE_HALO_WIDTH = 0.8;
    float FLARE_DISPERSAL = 0.9;
    vec3 CHROMA_DISTORT = vec3(0.004, -0.004, 0.0);

    vec2 sample_vector = vec2(0.5, 0.5)-uv * FLARE_DISPERSAL;
    vec2 halo_vector = normalize(sample_vector) * FLARE_HALO_WIDTH;
    vec3 tmp = vec3(0.0, 0.0, 0.0);
    vec3 result = 0.0;
    result.x = texture2D(glareTex, uv + halo_vector + halo_vector * CHROMA_DISTORT.x).x;
    result.y = texture2D(glareTex, uv + halo_vector + halo_vector * CHROMA_DISTORT.y).y;
    result.z = texture2D(glareTex, uv + halo_vector + halo_vector * CHROMA_DISTORT.z).z;
    for (int i = 0; i < NSAMPLES; ++i) {
        vec2 offset = sample_vector * float(i);
        tmp.x = texture2D(glareTex, uv + offset + offset  * CHROMA_DISTORT.x).x;
        tmp.y = texture2D(glareTex, uv + offset + offset  * CHROMA_DISTORT.y).y;
        tmp.z = texture2D(glareTex, uv + offset + offset  * CHROMA_DISTORT.z).z;
        result += tmp;
    }        
    result /= float(NSAMPLES); 
    gl_FragColor =vec4(result.xyz, 1.0);
    }
 