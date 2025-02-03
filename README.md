# **OT_Game_2024 - Game Design Document - SK**

This is my final project in OT
An idle game made in entierly in pygame

**Autor**: Erik Kováč

**Vybraná téma**: Four elements

---
## **1. __init__**
The proposed game serves as a demonstration for the subject of Object Technologies, with the goal of creating a functional game prototype as a project for the exam. The created game meets the requirements of the assigned topic (Four elements).
It's an idle clicker game made to be played on a single monitor computers while having the ability to multitask.

### **1.1 Inspiration**
<ins>**Cookie Clicker**</ins>

Cookie Clicker is an incremental, idle browser game created by French programmer Julien "Orteil" Thiennot. The game revolves around clicking a giant cookie to produce more cookies, which can then be used to purchase upgrades, buildings, and other items to automate cookie production. With its simple yet addictive gameplay, Cookie Clicker has become a popular example of the "clicker" or "idle game" genre, where players progress by performing repetitive actions or letting the game run on its own. Its charming visuals, quirky upgrades, and endless cookie-making mechanics have made it a beloved time-killer for players worldwide.

<ins>**Rusty's Retirement**</ins>

Rusty's Retirement is a casual, relaxing farming simulation game where players help Rusty, a retired robot, manage and grow a charming farm. The game focuses on automation and resource management, allowing players to plant crops, harvest resources, and upgrade their farm while enjoying a laid-back, low-pressure experience. With its pixel-art style and soothing gameplay, Rusty's Retirement is designed to be played in short sessions or as a secondary activity, making it perfect for unwinding. It combines the satisfaction of farming sims with the simplicity of idle games, offering a delightful escape for players of all ages.

### **1.2 Gameplay**
Elemental Village is a charming idle clicker game that runs in a compact, floating window, perfect for multitasking. Set in a magical world, players build and manage a village powered by elemental forces like fire, water, earth, and air. By clicking or automating resource collection, you can upgrade buildings, unlock new elements, and expand your village into a thriving elemental paradise. The game’s small, resizable window allows you to keep most of your screen free for other tasks, making it ideal for casual play while working or browsing. With its relaxing gameplay, enchanting visuals, and incremental progression, Elemental Village offers a delightful and unobtrusive gaming experience.

### **1.3 Software used**
- **Pygame-CE**: Basic game making toolkit (library) for python
- **PyCharm 2024**: Python IDE
- **Aseprite**: Pixel Art Paint

---
## **2. Concept**

### **2.2 Interpretation of the theme**
Elemental Village is, as the name suggest revolves around managing village in a magical place where people can harvest elemental power.
The village never stops growing, the Village must grow

### **2.4 Python Classes**
- **UI-Components/Managers**: custom UI components/managers ensure consistant look on almost any display size and aspect ratio, additionaly makes the UI development shorter
- **Sound Component**: sound components ensure easy and flexible way to run mp3 files
- **Data Handlers**: Data Handlers ensure easy and consistant way to access and mannage large data and (loading/saving)

---
## **3. Graphycs**

### **3.1 Interpretácia témy (Swarms - príklad témy)**
The game consists of two types of graphycs
- **Fully made by me**: These images are created by me using Aseprite
- **Parshly made by me**: These images are downloaded from openly available sources and then edited by me to fit into my art style
In short there are no images that were straight up downloaded and used

---
## **4. Sound**

### **4.1 Music**
The game uses royalty-free music that's synced with the main menu animation

---
## **5. Gaming expirience**

### **5.1 User Interface**
The game uses my custom UI components consisting of

- **Scene_Manager** : Manages all the scenes and currently selected scene, handles things like updates, emits, and more
- **Scene** : Specific scene containing all the Graphycal data a scene needs
- **Component_Manager** : Each Scene has one of these, Manages all the components (Buttons, Labels, Images, etc...) and handles their updating and emits
- **Component** : My suit of components consists of (Images, Texts, Buttons, many more)

### **5.2 Controls**
Controls are simply done with mouse by clicking on specific areas/buttons
but there is a posibility of traversing scene history (previously active scenes) using Mouse or Pressing ESC
To quit the game simply press SHIFT + ESC to return to menu and by presing it again you can safely quit the game.

---
