from __future__ import annotations

from traffic_expert_system.simulation.engine import SimulationEngine


class PygameSimulationView:
    WIDTH = 1220
    HEIGHT = 760
    ROAD = (58, 64, 70)
    GRASS = (36, 102, 64)
    WHITE = (240, 242, 245)
    MUTED = (190, 198, 205)
    RED = (210, 72, 72)
    YELLOW = (238, 192, 60)
    GREEN = (72, 190, 110)

    def __init__(self, engine: SimulationEngine) -> None:
        self.engine = engine
        self.paused = False
        self.speed = 1

    def run(self) -> None:
        try:
            import pygame
        except ImportError as error:
            raise RuntimeError("Для окна симуляции установите pygame: python -m pip install pygame") from error

        pygame.init()
        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Экспертная система управления перекрестком")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("arial", 18)
        small = pygame.font.SysFont("arial", 14)
        accumulator = 0.0
        running = True

        while running:
            elapsed = clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self.engine = SimulationEngine(self.engine.intersection, self.engine.scenario, self.engine.controller)
                    elif event.key == pygame.K_1:
                        self.speed = 1
                    elif event.key == pygame.K_5:
                        self.speed = 5
                    elif event.key == pygame.K_0:
                        self.speed = 10

            if not self.paused and not self.engine.finished:
                accumulator += elapsed * self.speed
                while accumulator >= 0.25 and not self.engine.finished:
                    self.engine.step()
                    accumulator -= 0.25

            self._draw(pygame, screen, font, small)
            pygame.display.flip()
        pygame.quit()

    def _draw(self, pygame, screen, font, small) -> None:
        screen.fill(self.GRASS)
        center_x, center_y = 410, 375
        road_width = 150
        pygame.draw.rect(screen, self.ROAD, (0, center_y - road_width // 2, 820, road_width))
        pygame.draw.rect(screen, self.ROAD, (center_x - road_width // 2, 0, road_width, self.HEIGHT))
        pygame.draw.rect(screen, self.WHITE, (center_x - 75, center_y - 75, 150, 150), 2)
        self._draw_lanes(pygame, screen, center_x, center_y)
        self._draw_signals(pygame, screen, center_x, center_y, font)
        self._draw_vehicles(pygame, screen, center_x, center_y)
        self._draw_panel(pygame, screen, font, small)

    def _draw_lanes(self, pygame, screen, center_x: int, center_y: int) -> None:
        line = (190, 190, 160)
        pygame.draw.line(screen, line, (0, center_y), (center_x - 75, center_y), 2)
        pygame.draw.line(screen, line, (center_x + 75, center_y), (820, center_y), 2)
        pygame.draw.line(screen, line, (center_x, 0), (center_x, center_y - 75), 2)
        pygame.draw.line(screen, line, (center_x, center_y + 75), (center_x, self.HEIGHT), 2)

    def _approach_is_green(self, approach: str) -> bool:
        state = self.engine.state
        if state.signal_color.value != "green":
            return False
        phase = state.current_phase
        return any(self.engine.intersection.lane_by_id[lane_id].approach == approach for lane_id in phase.allowed_lanes)

    def _draw_signals(self, pygame, screen, center_x: int, center_y: int, font) -> None:
        locations = {
            "north": (center_x - 98, center_y - 100),
            "south": (center_x + 98, center_y + 100),
            "east": (center_x + 100, center_y - 98),
            "west": (center_x - 100, center_y + 98),
        }
        for approach in self.engine.intersection.approaches:
            location = locations.get(approach, (center_x, center_y))
            color = self.YELLOW if self.engine.state.signal_color.value == "yellow" else (
                self.GREEN if self._approach_is_green(approach) else self.RED
            )
            pygame.draw.circle(screen, (25, 25, 25), location, 18)
            pygame.draw.circle(screen, color, location, 12)
            label = font.render(approach[0].upper(), True, self.WHITE)
            screen.blit(label, (location[0] - 6, location[1] - 48))

    def _draw_vehicles(self, pygame, screen, center_x: int, center_y: int) -> None:
        offsets = {
            "north": lambda index: (center_x - 36, center_y - 125 - index * 25),
            "south": lambda index: (center_x + 16, center_y + 105 + index * 25),
            "east": lambda index: (center_x + 105 + index * 25, center_y - 36),
            "west": lambda index: (center_x - 125 - index * 25, center_y + 16),
        }
        by_approach: dict[str, int] = {approach: 0 for approach in self.engine.intersection.approaches}
        for lane in self.engine.intersection.lanes:
            for vehicle in self.engine.state.queues[lane.id]:
                index = by_approach[lane.approach]
                by_approach[lane.approach] += 1
                if lane.approach not in offsets:
                    continue
                x, y = offsets[lane.approach](index)
                pygame.draw.rect(screen, (65, 148, 214), (x, y, 18, 12), border_radius=2)

    def _draw_panel(self, pygame, screen, font, small) -> None:
        panel_x = 850
        pygame.draw.rect(screen, (30, 34, 40), (panel_x, 0, self.WIDTH - panel_x, self.HEIGHT))
        state = self.engine.state
        lines = [
            ("Адаптивный светофор", font, self.WHITE),
            (f"Время: {state.time} с", font, self.MUTED),
            (f"Скорость: x{self.speed}" + ("  ПАУЗА" if self.paused else ""), font, self.MUTED),
            ("", small, self.WHITE),
            (f"Фаза: {state.current_phase.id}", font, self.WHITE),
            (f"Сигнал: {state.signal_color.value}", font, self.MUTED),
            (f"Длительность фазы: {state.phase_elapsed} с", font, self.MUTED),
            (f"Обслужено: {state.metrics.served_vehicles}", font, self.WHITE),
            (f"Очередь: {state.remaining_vehicles}", font, self.WHITE),
            ("", small, self.WHITE),
            ("Решение экспертной системы", font, self.WHITE),
        ]
        decision_text = state.last_decision.explanation if state.last_decision else "Ожидание первого такта."
        lines.extend((line, small, self.MUTED) for line in self._wrap(decision_text, 36))
        lines.append(("", small, self.WHITE))
        lines.append(("Space: пауза | R: сброс", small, self.MUTED))
        lines.append(("1/5/0: скорость | Esc: выход", small, self.MUTED))
        y = 30
        for text, active_font, color in lines:
            surface = active_font.render(text, True, color)
            screen.blit(surface, (panel_x + 24, y))
            y += 28 if active_font == font else 21

    @staticmethod
    def _wrap(text: str, width: int) -> list[str]:
        words, lines, current = text.split(), [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) > width and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        return lines + ([current] if current else [])
