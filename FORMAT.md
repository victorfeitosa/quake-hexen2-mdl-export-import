### MDL header
```c
struct mdl_header_t
{
  int ident;            /* magic number: "IDPO" */
  int version;          /* version: 6 */

  vec3_t scale;         /* scale factor */
  vec3_t translate;     /* translation vector */
  float boundingradius;
  vec3_t eyeposition;   /* eyes' position */

  int num_skins;        /* number of textures */
  int skinwidth;        /* texture width */
  int skinheight;       /* texture height */

  int num_verts;        /* number of vertices */
  int num_tris;         /* number of triangles */
  int num_frames;       /* number of frames */

  int synctype;         /* 0 = synchron, 1 = random */
  int flags;            /* state flag */
  float size;
};
```

### Skin
```c
struct mdl_skin_t
{
  int group;      /* 0 = single, 1 = group */
  GLubyte *data;  /* texture data */
};
```


### Group of skins
```c
struct mdl_groupskin_t
{
    int group;     /* 1 = group */
    int nb;        /* number of pics */
    float *time;   /* time duration for each pic */
    ubyte **data;  /* texture data */
};
```

### Texture coords
```c
struct mdl_texcoord_t
{
  int onseam;
  int s;
  int t;
};
```

### Triangle info
```c
struct mdl_triangle_t
{
  int facesfront;  /* 0 = backface, 1 = frontface */
  int vertex[3];   /* vertex indices */
};
```

### Hexen II Expansion Pack Triangle info
```c
struct mdl_triangle_t
{
  int facesfront;     /* 0 = backface, 1 = frontface */
  short vertex[3];    /* vertex indices */
  short stindex[3];   /* uv indices */
};
```

### Compressed vertex
```c
struct mdl_vertex_t
{
  unsigned char v[3];
  unsigned char normalIndex;
};
```

### Simple frame
```c
struct mdl_simpleframe_t
{
  struct mdl_vertex_t bboxmin; /* bouding box min */
  struct mdl_vertex_t bboxmax; /* bouding box max */
  char name[16];
  struct mdl_vertex_t *verts;  /* vertex list of the frame */
};
```

### Group of simple frames
```c
struct mdl_groupframe_t
{
  int type;                         /* !0 = group */
  struct mdl_vertex_t min;          /* min pos in all simple frames */
  struct mdl_vertex_t max;          /* max pos in all simple frames */
  float *time;                      /* time duration for each frame */
  struct mdl_simpleframe_t *frames; /* simple frame list */
};
```

