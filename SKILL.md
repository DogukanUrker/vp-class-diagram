---
name: vp-class-diagram
description: draw a uml class diagram of java code as an html page that looks exactly like visual paradigm (vp) - same blue boxes, text, straight lines and vp's exact arrowheads (white triangle for extends, blue for implements, white / black diamonds, multiplicity labels). use this whenever the user asks for a class diagram, uml diagram, "the diagram for this lab", a visual paradigm / vp style diagram, or wants to see how their java classes connect - even if they don't say "uml" or "vp". works great for design pattern homework (factory, decorator, observer, strategy, ...) and any other java code. also use it to change or fix a diagram.html made before.
---

# vp class diagram

this skill turns java code into `diagram.html`: a uml class diagram that looks like real visual paradigm output. the look is already fixed in `assets/renderer.html`. it was measured pixel by pixel from a real vp screenshot. so your job is only to:

1. describe the classes in a small json model
2. build the page with the script
3. check it and fix the layout
4. show it to the user

do not hand-write svg or change the renderer's style to "improve" it. the look was matched pixel by pixel to real vp output, and small drift (arrow size, dash length, padding) is easy to spot next to a real vp diagram.

## steps

1. **find the code.** usually it's `src/*.java` in the current project. read every file. you need the real fields, methods and `extends` / `implements` / `new` lines, not guesses.
2. **write the model** as json in your scratchpad, not in the project. the format and the rules are below.
3. **build:**
   ```bash
   python3 -I ~/.claude/skills/vp-class-diagram/scripts/build.py <model.json> <project>/diagram.html
   ```
   put `diagram.html` next to `src`, never inside it. projects like this are often handed in as a zip of `src/*.java`, so a file inside `src` could end up in the submission. the script checks the model first (unknown names, missing boxes, bad types) and tells you what to fix. then it takes a screenshot by itself with headless chrome. it writes `diagram.png` next to the html and prints any layout warnings. this way nobody has to take the screenshot by hand.
4. **check it** (see "checking"), fix the layout, and build again until it is clean.
5. **show it:** run `open <project>/diagram.html`, and tell the user where `diagram.png` is. then tell them in a few short lines what the diagram shows, and anything you left out on purpose.

if `diagram.html` already exists and the user wants a change, the old model is inside it, in the `<script id="model">` block. copy it out, edit it, and build again.

## the model

```json
{
  "title": "Factory Class Diagram",
  "classes": [
    { "name": "Car", "kind": "abstract",
      "attributes": ["-modelName : String"],
      "operations": ["#Car(modelName : String)", "+display()",
                     { "text": "#createCar(type : String) : Car", "abstract": true },
                     { "text": "+getCount() : int", "static": true }] }
  ],
  "layout": [
    [null, "CarManufacturer"],
    [{ "name": "Car", "span": 3 }]
  ],
  "sameWidth": [["ToyotaSedan", "ToyotaSUV"]],
  "relations": [
    { "from": "ToyotaSedan", "to": "Car", "type": "generalization" },
    { "from": "CarManufacturer", "to": "Car", "type": "dependency", "route": "right" }
  ]
}
```

- `kind`: `"class"` (default), `"abstract"` (name in italic) or `"interface"` (adds the `<<Interface>>` line). `"stereotype": "..."` sets a custom one.
- a row is a plain string, or an object with `"abstract": true` (italic) and/or `"static": true` (underlined).
- `layout` is a grid. each inner list is one row, from top to bottom. cells fill columns from left to right. a name or `null` (an empty cell) takes 1 column, and `{ "name": ..., "span": n }` takes n columns, with the box centered over them. a span can start anywhere in a row. every class must appear exactly once.
- `sameWidth` (optional) gives a group of boxes the same width, so a row of siblings looks neat.
- `relations[].type`: `generalization`, `realization`, `dependency`, `association`, `aggregation`, `composition`. for aggregation and composition, `from` is the whole (the class with the field) and `to` is the part. the diamond is drawn at `from`.
- `fromLabel` / `toLabel` (optional) put a multiplicity like `"1"` or `"0..*"` next to that end of the line.
- `"arrow": false` (optional) turns off the arrowhead of an `association`, for a plain line.
- `route` (optional, `"left"` / `"right"`) sends a long line around the side of the diagram instead of through it.
- `spacing` (optional) overrides `colGap`, `rowGap`, `linkGap`, `margin`.

full examples you can copy from:
- `examples/factory.json`: abstract classes, 9 subclasses in one row, a wide box spanning the bottom, a side route
- `examples/decorator.json`: a class that both extends and has a field of the same type (two lines between one pair)
- `examples/observer.json`: interfaces, realizations, an association, links between boxes in the same row. `Subject` -> `Observer` is a dependency because `registerObserver(o : Observer)` takes one as a parameter.
- `examples/order.json`: vp's own "order system" tutorial example. it shows aggregation, multiplicity labels, plain and navigable associations, and white generalization triangles.

## java to vp text

vp writes members without a space after the visibility sign, and leaves out `void`. follow that exactly, because it is what real vp output shows.

| java | vp text |
|---|---|
| `private String name;` | `-name : String` |
| `protected final double weight;` | `#weight : double` |
| `public static int count;` | `+count : int` with `"static": true` |
| package-private (no keyword) | `~name : String` |
| `public void display()` | `+display()` |
| `public Car orderCar(String type)` | `+orderCar(type : String) : Car` |
| `protected abstract Car createCar(String type);` | `#createCar(type : String) : Car` with `"abstract": true` |
| `public ToyotaSedan()` (constructor) | `+ToyotaSedan()` |
| `public static Logger getInstance()` | `+getInstance() : Logger` with `"static": true` |
| `List<Observer> observers` | `-observers : List<Observer>` |

- show every field, constructor and method that is written in the class. leave out ones it only inherits. don't add a constructor the code doesn't write (java's hidden default one).
- leave out `final` and `@Override`. vp doesn't show them by default.
- an `abstract class` always gets `"kind": "abstract"` (italic name), even if it has no abstract methods.
- interface methods are public, so they get `+`. they are not italic unless the user asks for it.

## which line to draw

| code | type | looks like |
|---|---|---|
| `class A extends B` | `generalization` A to B | solid line, white triangle at B |
| `class A implements I` | `realization` A to I | dashed line, blue triangle at I |
| `interface I extends J` | `generalization` I to J | solid line, white triangle at J |
| A has a field of type B (also `B[]`, `List<B>`) | `association` A to B | solid line, open arrow at B |
| A has a field of type B that is handed in from outside (constructor, setter, `register...`), and the lab or user wants "part of" shown | `aggregation` A to B | solid line, white diamond at A |
| A creates its own B (`new B()` in A's field or constructor), never hands it out, and the lab or user wants "owns" shown | `composition` A to B | solid line, black diamond at A |
| A only uses B: `new B()`, a parameter, a return type, a local variable | `dependency` A to B | dashed line, open arrow at B |

- for a field, `association` is the default. use `aggregation` / `composition` only when the lab doc, the teacher's example or the user asks for diamonds. design pattern books draw the same field both ways, so don't guess. say which one you used, so the user can switch.
- multiplicity: a list or array field gets `"toLabel": "0..*"`. don't invent labels for single fields unless the lab or the user wants them.

- a dependency is the weakest line. skip it when the two classes already have another line. also skip it when the target is already a parent or grandparent of the source. for example, `HighMemory(Server server)` needs no dependency to `Server`, because it already extends `Server` through `ResourceDecorator`.
- generalization / realization and association are different facts, so both can be drawn between the same pair. the decorator is the classic case: `ResourceDecorator extends Server` and also has a `Server` field, so it gets a triangle line and an association line. the renderer puts the two lines side by side. that's expected, and the has-a line is the heart of the pattern, so don't drop it.
- no lines to java library types (`String`, `Scanner`, `List`, ...).
- leave out the test / main class (the one with `public static void main`) and every line to or from it. it only runs the program and isn't part of the design, so it just adds noise.
- getting solid vs dashed right matters for grading. a lab with interfaces has dashed triangles. a lab with abstract classes has solid triangles. never copy the line style from an older lab. read it from the code.

## layout tips

- parents go above children: interfaces and abstract classes on top, the classes that extend them in the row below.
- put children in the columns under their parent, and center the parent with `null` cells or `span`. lines are straight, so a parent far to the side makes long diagonal lines.
- a box with a very long row (like a big constructor) works best alone in the bottom row with a `span` over the whole width.
- boxes that are linked and sit in the same row get extra space between them automatically.
- if a line would have to pass through another box, move one of the boxes, or use `"route": "right"` / `"left"`.

## checking

the build prints `warnings: none` or a list of problems: lines that cross a box, and too many arrowheads on one side of a box.

1. fix every warning (move boxes, add `null` cells, use `route`) and build again.
2. look at `diagram.png` with the Read tool. it is the exact diagram at 2x scale, so it shows what the user will see. look for long diagonal lines that would be shorter with a better layout, arrowheads that touch, and big empty areas.
3. to zoom in on small details like arrowheads, crop a copy into your scratchpad: `sips -c <height> <width> --cropOffset <y> <x> diagram.png --out <scratchpad>/crop.png`. png pixels are 2x the layout numbers.
4. if the build says `no screenshot` (no chrome found), the html is still fine. open it and ask the user to look at it instead.

## the style

these values live in `STYLE` and `TYPES` in `assets/renderer.html`. they were measured from a real vp diagram (a blue observer diagram) and from the 18 images in vp's official class diagram tutorial (visual-paradigm.com/guide/uml-unified-modeling-language/uml-class-diagram-tutorial):

- box fill `#7acff5`, 1px black border and black text
- arial 11px, class names bold 11px, 15px per row, 2px left padding
- name row is 15px tall, or 30px with a `<<stereotype>>` line
- each compartment is rows x 15px + 4px. a class with no members gets one empty 25px compartment.
- triangle: 13px long, 13px wide, 1px outline. **white** for generalization (extends), **box blue** for realization (implements). vp's own pictures show both. a diagram with only interfaces shows only blue triangles, so don't copy that look into a diagram with abstract classes.
- open arrow (dependency, association): 13px long, 6px out on each side
- diamond (aggregation white, composition black): 22px long, 13px wide, at the whole's end
- multiplicity labels: arial 11px, beside the end of the line, about 10px from the box (further when there's an arrowhead or diamond)
- dashes: 5px on, 5px off
- lines are straight. each line has its own arrowhead, and lines don't merge. vp's tutorial calls this "separate target" style and shows it as official.

if the user sends a new vp screenshot and wants the look changed, measure it the same way: load the image in a browser canvas and read the pixel colors and sizes, and match text widths against `ctx.measureText` to find the font size. one trap: in a vp screenshot, the lines touching a **selected** box (gray frame, corner handles) are drawn thick. that is a highlight, not the real style.

## not supported yet

line names and role names (like "line item"), notes, packages, and the "shared target" style where lines merge into one stem. if a lab needs one, tell the user and ask for a vp screenshot or svg export that shows it. then measure it and add it to the renderer, instead of guessing the look.

never add vp's "made with visual paradigm" watermark or logo. these diagrams aren't made with vp, so the badge would be a false claim.
