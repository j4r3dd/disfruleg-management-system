# Ubicuo AI - Ejemplos

## Ejemplo 1: Pedido Simple

```
2 kg de cebolla
```

**Resultado:**
```
✓ 2 kg de Cebolla Blanca (ID: 12)
```

---

## Ejemplo 2: Múltiples Productos

```
2 kg de cebolla
1 manojo de cilantro
0.5 kg de tomate
```

**Resultado:**
```
✓ 2 kg de Cebolla Blanca (ID: 12)
✓ 1 manojo de Cilantro (ID: 45)
✓ 0.5 kg de Tomate Rojo (ID: 78)
```

---

## Ejemplo 3: Orden Diferente

```
lechuga 3 pz
```

**Resultado:**
```
✓ 3 piezas de Lechuga Verde (ID: 23)
```

---

## Ejemplo 4: Decimales y Fracciones

```
0.5 kg de tomate
1/2 litro de leche
```

**Resultado:**
```
✓ 0.5 kg de Tomate Rojo (ID: 78)
✓ 0.5 litros de Leche Entera (ID: 56)
```

---

## Ejemplo 5: Producto No Encontrado

```
xyz 5 kg
```

**Resultado:**
```
⚠️ Producto "xyz" no encontrado
💡 ¿Quisiste decir "zanahoria"?
```

---

[Ver Guía Rápida →](guia.md)