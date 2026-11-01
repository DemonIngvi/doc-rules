1. **Story 1.1, AC1** — «Administrator входит и создаёт Project с Process → Project появляется в списке»
   Причина: нет данных (логин/пароль, имя Project, какой Process), не указан способ проверки (UI или API, какой список), «чистая установка» не задаёт время готовности.
   Переписать: «Given чистая установка, `docker compose up` завершён и `/health` вернул 200, есть Administrator `admin/<пароль из .env>`; When `POST /projects {name:"P1", processId:<Basic>}`; Then 201, и `GET /projects` содержит ровно один Project с name="P1" и этим processId».

2. **Story 1.1, AC2** — «пользователь без Role получает 404 на Work Item этого Project»
   Причина: не определены пользователь, Project и Work Item, эндпоинт. Неясно, почему 404, а не 403, и это ли ожидаемое поведение. Нет проверки, что для пользователя с Role тот же запрос успешен.
   Переписать: «Given Project P1 с Work Item id=W1 и пользователь U без Role в P1; When `GET /work-items/W1` от U; Then 404 с пустым телом данных о W1 (404 намеренно скрывает существование)».

3. **Story 1.1, AC3** — «Observer пытается изменить Work Item → API возвращает 403»
   Причина: «изменить» не конкретизировано (PATCH, смена State, удаление?), нет данных о Work Item и Project; не проверяется, что данные не изменились.
   Переписать: «Given Observer O в P1 и Work Item W1 (title="A"); When `PATCH /work-items/W1 {title:"B"}` от O; Then 403, и `GET /work-items/W1` возвращает title="A"». Повторить для DELETE и смены State или явно ограничить критерий одним действием.

4. **Story 1.2, AC1** — «связи сохраняются, а прогресс родителя считается по завершённому Effort»
   Причина: два разных утверждения в одном; формула прогресса не задана (процент? единицы Effort? что с нулевым Effort, с незавершёнными потомками), нет числовых данных. Не указано, в какой момент пересчитывается прогресс.
   Переписать: разделить. (a) «Then `GET` каждого элемента возвращает parentId предыдущего уровня». (b) «Given Feature с двумя Task по Effort 3 и 7, Task(3) в State Done; When запрос прогресса Feature; Then progress = 30% (3/10), пересчёт не позднее 1 с после смены State». Добавить кейс Effort=0.

5. **Story 1.2, AC2** — «запрос отклоняется с понятной причиной»
   Причина: «понятная причина» неизмерима; нет кода ответа, формата ошибки, эндпоинта.
   Переписать: «When `PATCH /work-items/{story}` с parentId=<Portfolio Epic>; Then 422, тело `{code:"INVALID_PARENT_TYPE", message}`, parentId у Story остаётся null».

6. **Story 1.2, AC3** — «попытка создать Task без User Story → Task не создаётся»
   Причина: нет кода ответа, непонятно, что значит «без» (parentId отсутствует, null, несуществующий id, id Feature); «не создаётся» не привязано к проверке.
   Переписать: «When `POST /work-items {type:"Task"}` без parentId (и отдельно с parentId=Feature); Then 422 `{code:"PARENT_REQUIRED"}` / `INVALID_PARENT_TYPE`, и количество Work Item в Project не изменилось».

7. **Story 1.2, AC4** — «указывает User Story или Feature → Bug связан не более чем с одним родителем»
   Причина: «или» неоднозначно; «не более чем» допускает и 0, и 1 — тест пройдёт при любом результате. Неясно, что при указании обоих родителей (ошибка или выбор одного).
   Переписать: три кейса: «parentId=Story → 201, parent=Story»; «parentId=Feature → 201, parent=Feature»; «переданы оба (parentStoryId и parentFeatureId) → 422 `MULTIPLE_PARENTS`, Bug не создан». Указать, допустим ли Bug без родителя.

8. **Story 1.3, AC1–AC2** — «запрещённый переход → 422 с причиной»; «Administrator удаляет его → система требует перенести Work Item»
   Причина: не задан Workflow (какие переходы разрешены), нет конкретной пары State; «с причиной» и «требует перенести» не имеют проверяемого результата (код, поле, статус удаления). Не сказано, что State остаётся прежним / что State не удалён.
   Переписать: «Given Workflow Story: New→Active→Done, Story S в New; When `POST /work-items/S/transition {to:"Done"}`; Then 422 `{code:"TRANSITION_NOT_ALLOWED", from:"New", to:"Done"}`, State S = New». Для удаления: «Given State Active с 2 Work Item; When `DELETE /states/Active` без `moveTo`; Then 409 `{code:"STATE_IN_USE", count:2}`, State существует; с `?moveTo=New` → 204, оба Work Item в State New».